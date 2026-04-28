import httpx
from app.core.config import settings
from app.ai.providers.base import BaseProvider

class OllamaProvider(BaseProvider):
    async def chat(self, messages: list[dict], model: str) -> str:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        async with httpx.AsyncClient(timeout=120) as client:
            result = await client.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json={"model": model, "prompt": prompt, "stream": False})
            result.raise_for_status()
            return result.json().get("response", "")
