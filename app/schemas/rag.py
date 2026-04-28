from pydantic import BaseModel, Field

class RAGQueryRequest(BaseModel):
    question: str
    provider: str | None = None
    model: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)

class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    provider: str
    model: str
