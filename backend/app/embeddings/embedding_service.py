from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbeddingService:
    def __init__(self):
        print(f"[EmbeddingService] Loading model: {settings.EMBEDDING_MODEL_NAME}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        # Verify dimension
        self.dimension = len(self.model.encode("test"))
        print(f"[EmbeddingService] Model dimension is {self.dimension}")

    def embed_text(self, text: str):
        return self.model.encode(text, show_progress_bar=False).tolist()
        
    def embed_texts(self, texts: list):
        return self.model.encode(texts, show_progress_bar=False).tolist()

embedding_service = EmbeddingService()
