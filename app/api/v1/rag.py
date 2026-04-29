from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.rag.service import query_rag

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(payload: RAGQueryRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return await query_rag(db, user, payload.question, payload.provider, payload.model, payload.top_k, payload.include_web_search)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
