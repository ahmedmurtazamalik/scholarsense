"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./slr_db.sqlite"

    # Auth
    JWT_SECRET: str = "your-fallback-super-secret-key-for-jwt"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # LLM
    GROQ_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.1-8b-instant"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Vector Store
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    VECTOR_SEARCH_TOP_K: int = 5

    # Pipeline Thresholds
    SCREENING_THRESHOLD: float = 0.6
    EVALUATION_THRESHOLD: float = 0.55

    # Zotero variables moved to User database model for multi-tenancy.

    # Storage
    UPLOAD_DIR: str = "./uploads"

    # App
    APP_NAME: str = "SLR Platform"
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
