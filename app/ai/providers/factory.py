from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.ollama_provider import OllamaProvider

class ProviderFactory:
    @staticmethod
    def get(provider: str):
        provider = provider.lower()
        if provider == "openai":
            return OpenAIProvider()
        if provider in {"anthropic", "claude"}:
            return AnthropicProvider()
        if provider == "gemini":
            return GeminiProvider()
        if provider == "ollama":
            return OllamaProvider()
        raise ValueError(f"Unknown provider: {provider}")
