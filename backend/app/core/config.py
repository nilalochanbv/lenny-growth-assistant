import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres@localhost:5432/lenny_growth_db"
    )
    
    # Local Model (Ollama)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
    OLLAMA_TIMEOUT_SECONDS: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "90.0"))
    
    # Cloud Models (Gemini / Anthropic / OpenAI)
    CLOUD_PROVIDER: str = os.getenv("CLOUD_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CLOUD_MODEL_NAME: str = os.getenv("CLOUD_MODEL_NAME", "gemini-2.5-flash")
    
    # Default Provider ('local' or 'cloud')
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "local")
    
    # RAG Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    MIN_RELEVANCE_SCORE: float = float(os.getenv("MIN_RELEVANCE_SCORE", "0.22"))
    
    # Data directories
    TRANSCRIPTS_DATA_DIR: str = os.getenv(
        "TRANSCRIPTS_DATA_DIR", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/transcripts"))
    )

settings = Settings()
