import os
from dotenv import load_dotenv
from .run_rag import PDFVectorizer
load_dotenv()

def query_rag(key_words):
    # Configurações
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME")
    
    # Inicializar vetorizador
    vectorizer = PDFVectorizer(
        chroma_db_path=CHROMA_DB_PATH,
        collection_name=COLLECTION_NAME
    )
    
    response = []
     
    if key_words.strip():
        results = vectorizer.search_documents(key_words, n_results=20)
            
        print(f"\nResultados para '{key_words}':")
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0], 
            results['distances'][0]
        )):
            response.append(metadata['filename'] + " - " + doc)

    return response

        
""" if __name__ == "__main__":
    query_rag()      """           