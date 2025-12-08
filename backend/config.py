"""
Configuration module for the LangGraph Multi-Agent System.
Loads environment variables and defines application constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Google Gemini API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    
    # Pinecone Index Names
    PINECONE_PAPERS_INDEX = os.getenv("PINECONE_PAPERS_INDEX", "lecture-rag-index")
    PINECONE_SLIDES_INDEX = os.getenv("PINECONE_SLIDES_INDEX", "lecture-slides-index")
    
    # Legacy support - if old PINECONE_INDEX_NAME is set, use it for papers
    if os.getenv("PINECONE_INDEX_NAME"):
        PINECONE_PAPERS_INDEX = os.getenv("PINECONE_INDEX_NAME")
    
    # Embedding Model
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Flask Settings
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # RAG Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    
    # Pinecone Namespaces
    NAMESPACE_TRANSCRIPT = "transcript"
    NAMESPACE_SLIDES = "slides"
    NAMESPACE_PAPERS = "papers"
    
    # LLM Configuration
    LLM_MODEL = "gpt-4o-mini"  # Using OpenAI instead of Gemini
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 2048
    
    # Agent Configuration
    MAX_CONVERSATION_HISTORY = 10  # Number of previous messages to keep in context
    TIMESTAMP_CONTEXT_WINDOW = 300  # Seconds before/after current timestamp to search
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        required_vars = [
            ("GOOGLE_API_KEY", cls.GOOGLE_API_KEY),
            ("PINECONE_API_KEY", cls.PINECONE_API_KEY),
        ]
        
        # OpenAI is optional (can use Google Gemini instead)
        if not cls.OPENAI_API_KEY:
            print("Note: OPENAI_API_KEY not set. Using Google Gemini for embeddings.")
        
        missing = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Please check your .env file."
            )
        
        return True


# Validate configuration on import
if __name__ != "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(f"Warning: {e}")
