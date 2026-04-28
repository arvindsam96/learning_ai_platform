from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

class PineconeStore:
    def __init__(self):
        if not settings.PINECONE_API_KEY:
            raise RuntimeError("PINECONE_API_KEY is not configured")
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.PINECONE_DIMENSION
        self._ensure_index()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self):
        existing = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name not in existing:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud=settings.PINECONE_CLOUD, region=settings.PINECONE_REGION),
            )

    def upsert(self, vectors: list[dict], namespace: str):
        self.index.upsert(vectors=vectors, namespace=namespace)

    def query(self, vector: list[float], namespace: str, top_k: int = 5):
        return self.index.query(vector=vector, namespace=namespace, top_k=top_k, include_metadata=True)

    def delete_by_filter(self, namespace: str, document_id: int):
        self.index.delete(namespace=namespace, filter={"document_id": {"$eq": document_id}})
