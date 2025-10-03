from flask import Blueprint, request, jsonify
from .request_test import extrair_palavras_chave, request_gemini
from .query_rag import query_rag

bp = Blueprint('api', __name__)

@bp.route('/ask-rag', methods=['POST'])
def ask_gemini_question():
    data = request.get_json()
    question = data.get('question', '')
    key_words = extrair_palavras_chave(question)
    
    # Consulta rag
    context = query_rag(key_words)
    
    # Gera resposta
    response = request_gemini(question, context)
    
    return jsonify(response)
    #return jsonify({'key_words': key_words, 'context': context})


def create_routes(app):
    app.register_blueprint(bp)