from anthropic import AsyncAnthropic
from app.core.config import settings
from app.ai.providers.base import BaseProvider

class AnthropicProvider(BaseProvider):
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def chat(self, messages: list[dict], model: str) -> str:
        system = ""
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system += m["content"] + "\n"
            else:
                user_messages.append({"role": m["role"], "content": m["content"]})
        result = await self.client.messages.create(model=model, max_tokens=2048, system=system or None, messages=user_messages)
        return result.content[0].text
