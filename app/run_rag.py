import os
import chromadb
from chromadb.config import Settings
import PyPDF2
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib
from typing import List, Dict
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFVectorizer:
    def __init__(self, 
                 chroma_db_path: str = "./chroma_db",
                 collection_name: str = "normativos",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Inicializa o vetorizador de PDFs
        
        Args:
            chroma_db_path: Caminho para o banco ChromaDB
            collection_name: Nome da coleção
            embedding_model: Modelo de embedding a ser usado
        """
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_db_path)
        
        # Carregar modelo de embedding
        logger.info(f"Carregando modelo de embedding: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Configurar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2048,
            chunk_overlap=20,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Criar ou obter coleção
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "PDF documents for RAG"}
        )
        
        logger.info(f"Coleção '{collection_name}' inicializada com {self.collection.count()} documentos")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrai texto de um arquivo PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Texto extraído do PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():  # Só adiciona se a página tem texto
                            text += f"\n--- Página {page_num + 1} ---\n"
                            text += page_text
                    except Exception as e:
                        logger.warning(f"Erro ao extrair página {page_num + 1} de {pdf_path}: {e}")
                        continue
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Erro ao processar PDF {pdf_path}: {e}")
            return ""

    def create_document_id(self, file_path: str, chunk_index: int) -> str:
        """
        Cria um ID único para o documento baseado no caminho e índice do chunk
        
        Args:
            file_path: Caminho do arquivo
            chunk_index: Índice do chunk
            
        Returns:
            ID único do documento
        """
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        filename = Path(file_path).stem
        return f"{filename}_{file_hash}_chunk_{chunk_index}"

    def process_single_pdf(self, pdf_path: str) -> int:
        """
        Processa um único arquivo PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Número de chunks processados
        """
        logger.info(f"Processando: {pdf_path}")
        
        # Extrair texto
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"Nenhum texto extraído de {pdf_path}")
            return 0
        
        # Dividir em chunks
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Documento dividido em {len(chunks)} chunks")
        
        # Preparar dados para inserção
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:  # Pular chunks muito pequenos
                continue
                
            doc_id = self.create_document_id(pdf_path, i)
            
            # Verificar se já existe
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing['ids']:
                    logger.info(f"Chunk {doc_id} já existe, pulando...")
                    continue
            except:
                pass  # Chunk não existe, continuar
            
            documents.append(chunk)
            metadatas.append({
                "source": pdf_path,
                "filename": Path(pdf_path).name,
                "chunk_index": i,
                "chunk_size": len(chunk),
                "total_chunks": len(chunks)
            })
            ids.append(doc_id)
        
        if not documents:
            logger.warning(f"Nenhum chunk válido encontrado em {pdf_path}")
            return 0
        
        # Gerar embeddings
        logger.info(f"Gerando embeddings para {len(documents)} chunks...")
        embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
        
        # Inserir no ChromaDB
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✅ {len(documents)} chunks inseridos com sucesso!")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Erro ao inserir chunks no ChromaDB: {e}")
            return 0

    def process_pdf_directory(self, directory_path: str) -> Dict[str, int]:
        """
        Processa todos os PDFs em um diretório
        
        Args:
            directory_path: Caminho do diretório
            
        Returns:
            Dicionário com estatísticas do processamento
        """
        directory = Path(directory_path)
        pdf_files = list(directory.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"Nenhum arquivo PDF encontrado em {directory_path}")
            return {}
        
        logger.info(f"Encontrados {len(pdf_files)} arquivos PDF")
        
        results = {}
        total_chunks = 0
        
        for pdf_file in pdf_files:
            try:
                chunks_processed = self.process_single_pdf(str(pdf_file))
                results[pdf_file.name] = chunks_processed
                total_chunks += chunks_processed
                
            except Exception as e:
                logger.error(f"Erro ao processar {pdf_file}: {e}")
                results[pdf_file.name] = 0
        
        logger.info(f"🎉 Processamento concluído! Total de chunks: {total_chunks}")
        return results

    def search_documents(self, query: str, n_results: int = 5) -> Dict:
        """
        Busca documentos similares à query
        
        Args:
            query: Texto da consulta
            n_results: Número de resultados
            
        Returns:
            Resultados da busca
        """
        query_embedding = self.embedding_model.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        return results

    def get_collection_stats(self) -> Dict:
        """
        Retorna estatísticas da coleção
        
        Returns:
            Estatísticas da coleção
        """
        count = self.collection.count()
        
        if count > 0:
            # Pegar uma amostra para análise
            sample = self.collection.get(limit=min(100, count), include=['metadatas'])
            
            sources = set()
            total_chunks = 0
            
            for metadata in sample['metadatas']:
                sources.add(metadata.get('filename', 'unknown'))
                total_chunks += 1
            
            return {
                "total_documents": count,
                "unique_sources": len(sources),
                "sample_sources": list(sources)[:10]  # Primeiros 10
            }
        
        return {"total_documents": 0, "unique_sources": 0, "sample_sources": []}

def main():
    """
    Função principal - exemplo de uso
    """
    # Configurações
    PDF_DIRECTORY = "./normativos"  # Altere para o seu diretório
    CHROMA_DB_PATH = "./chroma_db"
    COLLECTION_NAME = "normativos_collection"
    
    # Criar diretório se não existir
    os.makedirs(PDF_DIRECTORY, exist_ok=True)
    
    # Inicializar vetorizador
    vectorizer = PDFVectorizer(
        chroma_db_path=CHROMA_DB_PATH,
        collection_name=COLLECTION_NAME
    )
    
    # Mostrar estatísticas atuais
    stats = vectorizer.get_collection_stats()
    print(f"\n📊 Estatísticas atuais da coleção:")
    print(f"   Total de documentos: {stats['total_documents']}")
    print(f"   Fontes únicas: {stats['unique_sources']}")
    
    # Processar PDFs
    print(f"\n🔄 Processando PDFs do diretório: {PDF_DIRECTORY}")
    results = vectorizer.process_pdf_directory(PDF_DIRECTORY)
    
    # Mostrar resultados
    print(f"\n📋 Resultados do processamento:")
    for filename, chunks in results.items():
        status = "✅" if chunks > 0 else "❌"
        print(f"   {status} {filename}: {chunks} chunks")
    
    # Estatísticas finais
    final_stats = vectorizer.get_collection_stats()
    print(f"\n📊 Estatísticas finais:")
    print(f"   Total de documentos: {final_stats['total_documents']}")
    print(f"   Fontes únicas: {final_stats['unique_sources']}")
    
    # Exemplo de busca
    if final_stats['total_documents'] > 0:
        print(f"\n🔍 Teste de busca:")
        query = input("Digite uma consulta para testar a busca: ")
        if query.strip():
            results = vectorizer.search_documents(query, n_results=3)
            
            print(f"\nResultados para '{query}':")
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            )):
                print(f"\n{i+1}. Similaridade: {1-distance:.3f}")
                print(f"   Fonte: {metadata['filename']}")
                print(f"   Chunk: {metadata['chunk_index']}")
                print(f"   Texto: {doc[:200]}...")

if __name__ == "__main__":
    main()