from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.ai.service import run_chat

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        messages = [m.model_dump() for m in payload.messages]
        return await run_chat(db, user, payload.provider, payload.model, messages)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
