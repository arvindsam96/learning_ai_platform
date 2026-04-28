import asyncio
import google.generativeai as genai
from app.core.config import settings
from app.ai.providers.base import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        genai.configure(api_key=settings.GEMINI_API_KEY)

    async def chat(self, messages: list[dict], model: str) -> str:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        gemini = genai.GenerativeModel(model)
        result = await asyncio.to_thread(gemini.generate_content, prompt)
        return result.text
