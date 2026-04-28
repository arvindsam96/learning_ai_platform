from openai import AsyncOpenAI
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required for embeddings")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL

    async def embed_text(self, text: str) -> list[float]:
        result = await self.client.embeddings.create(model=self.model, input=text)
        return result.data[0].embedding

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        result = await self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in result.data]
