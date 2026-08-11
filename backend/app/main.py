import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add current folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.chat_routes import router as chat_router

app = FastAPI(
    title="College RAG Chatbot API",
    description="Enterprise RAG System powered by FastAPI, React, MinIO, MongoDB, Qdrant Vector Store, and local Ollama model.",
    version="2.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows local React dev server on any port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "College RAG Chatbot API",
        "version": "2.0.0",
        "llm_model": config.LLM_MODEL_NAME,
        "embedding_model": config.EMBEDDING_MODEL_NAME
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "mongo_db": config.MONGO_DB_NAME,
        "minio_bucket": config.MINIO_BUCKET,
        "collection_name": config.COLLECTION_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
