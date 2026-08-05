import uuid
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import config

class VectorStore:
    def __init__(self, storage_path: str = config.QDRANT_STORAGE_PATH, collection_name: str = config.COLLECTION_NAME):
        self.storage_path = storage_path
        self.collection_name = collection_name
        
        # Initialize Sentence Transformer Embedding Model
        print(f"[VectorStore] Loading embedding model '{config.EMBEDDING_MODEL_NAME}'...")
        try:
            self.embedder = SentenceTransformer(config.EMBEDDING_MODEL_NAME, local_files_only=config.LOCAL_FILES_ONLY)
        except Exception as e:
            if config.LOCAL_FILES_ONLY:
                print(f"[Warning] Failed to load embedding model locally ({e}). Attempting download...")
                self.embedder = SentenceTransformer(config.EMBEDDING_MODEL_NAME, local_files_only=False)
            else:
                raise e

        # Determine vector size dynamically
        dummy_vector = self.embedder.encode("test string")
        self.vector_dim = len(dummy_vector)
        print(f"[VectorStore] Embedding dimension: {self.vector_dim}")

        # Initialize Local Qdrant Client
        print(f"[VectorStore] Initializing Qdrant at '{self.storage_path}'...")
<<<<<<< HEAD
        self.client = QdrantClient(url=config.QDRANT_URL,
    api_key=config.QDRANT_API_KEY)
=======
        self.client = QdrantClient(path=self.storage_path)
>>>>>>> 49672135256fd1aea9c9b17b20fad1fba6a642eb

        self._ensure_collection()

    def _ensure_collection(self):
        """Creates the Qdrant collection if it doesn't already exist."""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            print(f"[VectorStore] Creating Qdrant collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_dim,
                    distance=Distance.COSINE
                )
            )
            print(f"[VectorStore] Collection '{self.collection_name}' created.")

    def add_documents(self, records: List[Dict[str, Any]]) -> int:
        """Encodes document text chunks and upserts them into Qdrant."""
        if not records:
            print("[VectorStore] No records provided for indexing.")
            return 0

        print(f"[VectorStore] Encoding {len(records)} chunks...")
        texts = [r["text"] for r in records]
        embeddings = self.embedder.encode(texts, show_progress_bar=True)

        points = []
        for idx, (record, vector) in enumerate(zip(records, embeddings)):
            point_id = str(uuid.uuid4())
            payload = {
                "text": record["text"],
                "source": record.get("source", ""),
                "filename": record.get("filename", ""),
                "chunk_index": record.get("chunk_index", 0),
                "chunk_id": record.get("chunk_id", f"chunk_{idx}")
            }
            points.append(PointStruct(id=point_id, vector=vector.tolist(), payload=payload))

        print(f"[VectorStore] Upserting {len(points)} points into Qdrant...")
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"[VectorStore] Ingestion complete! Total points: {len(points)}")
        return len(points)

    def search(self, query: str, top_k: int = config.TOP_K) -> List[Dict[str, Any]]:
        """Encodes a user query and searches Qdrant for top_k relevant context matches."""
        query_vector = self.embedder.encode(query).tolist()
        
        # Use query_points for qdrant-client 1.10+
        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            )
            results = response.points
        else:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )

        retrieved = []
        for res in results:
            retrieved.append({
                "score": res.score,
                "text": res.payload.get("text", ""),
                "source": res.payload.get("source", ""),
                "filename": res.payload.get("filename", "")
            })
        return retrieved

if __name__ == "__main__":
    vs = VectorStore()
    print("VectorStore successfully initialized.")
