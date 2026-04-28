import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.providers.factory import ProviderFactory
from app.core.config import settings
from app.db.models import UsageLog, User

FALLBACKS = ["openai", "anthropic", "gemini", "ollama"]
DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "gemini": "gemini-1.5-flash",
    "ollama": "llama3.1",
}

async def run_chat(db: AsyncSession, user: User | None, provider: str | None, model: str | None, messages: list[dict]) -> dict:
    start = time.time()
    selected_provider = provider or settings.DEFAULT_PROVIDER
    selected_model = model or settings.DEFAULT_MODEL or DEFAULT_MODELS.get(selected_provider, "gpt-4o-mini")
    fallback_used = False
    last_error = None
    for p in [selected_provider] + [x for x in FALLBACKS if x != selected_provider]:
        m = selected_model if p == selected_provider else DEFAULT_MODELS[p]
        try:
            llm = ProviderFactory.get(p)
            response = await llm.chat(messages, m)
            latency_ms = round((time.time() - start) * 1000, 2)
            db.add(UsageLog(user_id=user.id if user else None, provider=p, model=m, endpoint="/ai/chat", latency_ms=latency_ms))
            await db.commit()
            return {"provider": p, "model": m, "response": response, "latency_ms": latency_ms, "fallback_used": fallback_used}
        except Exception as exc:
            fallback_used = True
            last_error = exc
            continue
    raise RuntimeError(f"All providers failed: {last_error}")
