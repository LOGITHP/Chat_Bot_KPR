import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
DATA_DIR = STORAGE_DIR / "data"
MINIO_LOCAL_STORAGE = STORAGE_DIR / "minio_data"
QDRANT_STORAGE_PATH = str(STORAGE_DIR / "qdrant_storage")

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
MINIO_LOCAL_STORAGE.mkdir(parents=True, exist_ok=True)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "college_chatbot_db")

# MinIO Object Storage Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "college-documents")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Qdrant Vector DB Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "https://dbaf849d-c6d7-42b9-90a6-623d134cf23c.australia-southeast1-0.gcp.cloud.qdrant.io")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MWIyMTJiN2QtMDI0Mi00ZGIyLWI0MWYtZGU3MTMzMGU2MzAzIn0.5i9eeCpoFXGKyqzMfU4kQaGT3_hxvXhIJtJtRqZN-LU")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "college_knowledge")

# HuggingFace Embedding Model
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-base-en-v1.5")
LOCAL_FILES_ONLY = os.getenv("LOCAL_FILES_ONLY", "false").lower() == "true"

# RAG & Chunking Parameters
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("TOP_K", "3"))

# Ollama LLM Configuration (OpenAI-Compatible endpoint)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen2.5:7b")

# JWT Security
SECRET_KEY = os.getenv("SECRET_KEY", "college-chatbot-secret-key-super-secure-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours
