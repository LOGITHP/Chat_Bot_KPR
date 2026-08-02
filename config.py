import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
QDRANT_STORAGE_PATH = str(BASE_DIR / "qdrant_storage")

EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"
# Set to True if local files only, False if download allowed
LOCAL_FILES_ONLY = True

COLLECTION_NAME = "college_knowledge"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL_NAME = "qwen/qwen3.6-27b"
