"""
Configuration file for GenAI PYQ Assistant
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', True)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data/db.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Vector Store
    FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', 'data/vector_store.faiss')
    VECTOR_METADATA_PATH = os.getenv('VECTOR_METADATA_PATH', 'data/vector_store.pkl')
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
    OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', 300))
    
    # Embedding Model
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    
    # RAG Configuration
    RAG_TOP_K = int(os.getenv('RAG_TOP_K', 3))
    RAG_CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', 500))
    RAG_CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', 50))
    
    # Subjects
    SUBJECTS = ['DBMS', 'DS', 'ML', 'CN', 'OS']
    
    # Upload paths
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
    
    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
