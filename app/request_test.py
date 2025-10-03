import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

def extrair_palavras_chave(prompt):
    instruct = "Extraia e retorne somente as palavras-chave da seguinte pergunta: " + prompt
    response = model.generate_content(instruct)
    return response.text

def request_gemini(prompt, result_rag):
    instruct = f"""
        Você é um assistente especializado em análise de documentos e deve responder perguntas baseando-se exclusivamente nas informações fornecidas.

        **INSTRUÇÕES DE ANÁLISE:**

        1. **Compreensão da Pergunta:**
        - Identifique TODOS os elementos solicitados na pergunta do usuário
        - Determine se a pergunta tem múltiplas partes ou aspectos
        - Note palavras-chave específicas que indicam o tipo de informação desejada

        2. **Análise Completa dos Dados:**
        - Examine TODA a informação disponível em 'result_rag'
        - Procure por informações diretas E indiretas relacionadas à pergunta
        - Identifique conexões entre diferentes partes dos dados que possam complementar a resposta

        3. **Construção da Resposta:**
        - Responda a TODOS os aspectos da pergunta do usuário
        - Organize as informações de forma lógica e estruturada
        - Use formatação clara (tópicos, subtítulos) quando apropriado
        - Inclua detalhes relevantes, não apenas informações superficiais

        **PERGUNTA DO USUÁRIO:** {prompt}

        **DADOS DISPONÍVEIS:** {result_rag}

        **DIRETRIZES DE RESPOSTA:**

        **FAÇA:**
        - Base sua resposta EXCLUSIVAMENTE nas informações de 'result_rag'
        - Forneça uma resposta completa e detalhada
        - Cite a fonte/origem das informações sempre que possível
        - Use toda informação relevante disponível, não apenas a primeira encontrada
        - Estruture a resposta de forma clara e organizada

        **NÃO FAÇA:**
        - Adicionar informações que não estejam em 'result_rag'
        - Dar respostas parciais quando há mais informação disponível
        - Ignorar partes da pergunta que podem ser respondidas com os dados fornecidos

        **CASO DE INFORMAÇÃO INSUFICIENTE:**
        Se alguma parte da pergunta não puder ser respondida com base em 'result_rag', indique especificamente qual informação não foi encontrada, mas responda completamente as partes que podem ser respondidas.

        **FORMATO DE RESPOSTA:**
        Estruture sua resposta de forma clara, incluindo:
        - Resposta direta à pergunta
        - Detalhes e contexto relevantes
        - Fonte das informações (quando identificável)
    """
    
    try:
        response = model.generate_content(instruct)
        return response.text
    except Exception as e:
        raise

""" if __name__ == "__main__":
    prompt = "Considere a pergunta e extraia somente as palavras-chave."
    resposta = gerar_resposta(prompt) # type: ignore
    print(resposta) """