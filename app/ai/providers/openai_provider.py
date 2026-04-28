from openai import AsyncOpenAI
from app.core.config import settings
from app.ai.providers.base import BaseProvider

class OpenAIProvider(BaseProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(self, messages: list[dict], model: str) -> str:
        result = await self.client.chat.completions.create(model=model, messages=messages)
        return result.choices[0].message.content or ""
