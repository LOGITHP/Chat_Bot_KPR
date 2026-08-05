import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
QDRANT_STORAGE_PATH = str(BASE_DIR / "qdrant_storage")
QDRANT_URL = "https://dbaf849d-c6d7-42b9-90a6-623d134cf23c.australia-southeast1-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MWIyMTJiN2QtMDI0Mi00ZGIyLWI0MWYtZGU3MTMzMGU2MzAzIn0.5i9eeCpoFXGKyqzMfU4kQaGT3_hxvXhIJtJtRqZN-LU"


EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"
# Set to True if local files only, False if download allowed
LOCAL_FILES_ONLY = True

COLLECTION_NAME = "college_knowledge"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

# OpenAI-compatible LLM configuration (Supports local Ollama, OpenAI API, Groq, etc.)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen2.5:7b")

