from pydantic import BaseModel, Field
from typing import Literal

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"] = "user"
    content: str

class ChatRequest(BaseModel):
    provider: str | None = None
    model: str | None = None
    messages: list[ChatMessage]

class ChatResponse(BaseModel):
    provider: str
    model: str
    response: str
    latency_ms: float
    fallback_used: bool = False
