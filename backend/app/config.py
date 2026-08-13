import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "campus_assistant_db"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "campus-documents"
    MINIO_SECURE: bool = False

    # Qdrant — supports both naming conventions used across .env and docker-compose
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "campus_documents"   # fallback default
    COLLECTION_NAME: str = ""                      # from .env: COLLECTION_NAME
    QDRANT_API_KEY: str = ""

    # LLM — supports both naming conventions
    # .env uses: OPENAI_BASE_URL / OPENAI_API_KEY / LLM_MODEL_NAME
    OPENAI_BASE_URL: str = "http://localhost:11434/v1"
    OPENAI_API_KEY: str = "ollama"
    LLM_MODEL_NAME: str = "qwen2.5:7b"
    # Legacy / docker-compose keys kept for backward compatibility
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = ""                         # prefer LLM_MODEL_NAME

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    LOCAL_FILES_ONLY: bool = False

    # Chunking
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    MIN_CHUNK_SIZE: int = 100
    MAX_CHUNK_SIZE: int = 2000

    # Security — support both JWT_SECRET_KEY and SECRET_KEY
    JWT_SECRET_KEY: str = "secret"
    SECRET_KEY: str = ""       # from .env: SECRET_KEY
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GUEST_SESSION_TTL_HOURS: int = 2

    # App Config — include Vite dev server origins
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    MAX_UPLOAD_SIZE_MB: int = 50
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def effective_collection(self) -> str:
        """Returns the correct Qdrant collection name, preferring COLLECTION_NAME from .env."""
        return self.COLLECTION_NAME or self.QDRANT_COLLECTION

    @property
    def effective_llm_base_url(self) -> str:
        """Returns the LLM base URL, preferring OPENAI_BASE_URL from .env."""
        if self.OPENAI_BASE_URL and "11434" in self.OPENAI_BASE_URL:
            return self.OPENAI_BASE_URL
        return f"{self.OLLAMA_URL}/v1"

    @property
    def effective_model_name(self) -> str:
        """Returns the LLM model name, preferring LLM_MODEL_NAME from .env."""
        return self.LLM_MODEL_NAME or self.OLLAMA_MODEL or "qwen2.5:7b"

    @property
    def effective_api_key(self) -> str:
        """Returns the LLM API key."""
        return self.OPENAI_API_KEY or "ollama"

settings = Settings()
