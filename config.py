import os

class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    TESTING = os.getenv('TESTING', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    JSONIFY_PRETTYPRINT_REGULAR = True
    CHROMA_DB_PATH=os.getenv('CHROMA_DB_PATH')
    COLLECTION_NAME=os.getenv('COLLECTION_NAME')
    GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL=os.getenv('GEMINI_MODEL')
