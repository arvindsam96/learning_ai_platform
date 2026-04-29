from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PromptBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    prompt_type: str = Field(..., description="Type of prompt: 'system', 'user', 'rag_system', etc.")

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    prompt_type: Optional[str] = None
    is_active: Optional[bool] = None

class PromptResponse(PromptBase):
    id: int
    version: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PromptListResponse(BaseModel):
    prompts: list[PromptResponse]
    total: int
