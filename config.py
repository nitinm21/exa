import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    EXA_API_KEY = os.getenv('EXA_API_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # RAG context window sizes (in tokens)
    CONTEXT_WINDOWS = {
        '4K': 4096,
        '8K': 8192,
        '16K': 16384,
        '32K': 32768
    }

    # Default search settings
    DEFAULT_MAX_RESULTS = 5
