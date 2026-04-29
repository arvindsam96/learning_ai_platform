from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse, PromptListResponse
from app.ai.service import run_chat
from app.ai.prompt_service import PromptService

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        messages = [m.model_dump() for m in payload.messages]
        return await run_chat(db, user, payload.provider, payload.model, messages)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# Prompt management endpoints
@router.post("/prompts", response_model=PromptResponse)
async def create_prompt(
    prompt_data: PromptCreate, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Create a new prompt version"""
    try:
        return await PromptService.create_prompt(db, prompt_data, user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/prompts", response_model=PromptListResponse)
async def list_prompts(
    prompt_type: str = None,
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List prompts with optional filtering"""
    try:
        prompts, total = await PromptService.get_prompts(db, prompt_type, is_active, skip, limit)
        return PromptListResponse(prompts=prompts, total=total)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a specific prompt by ID"""
    try:
        prompt = await PromptService.get_prompt_by_id(db, prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.put("/prompts/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt_data: PromptUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update a prompt (creates new version)"""
    try:
        prompt = await PromptService.update_prompt(db, prompt_id, prompt_data, user)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/prompts/{prompt_id}/activate")
async def activate_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Activate a prompt version"""
    try:
        success = await PromptService.activate_prompt(db, prompt_id)
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return {"message": "Prompt activated successfully"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/prompts/{prompt_id}/deactivate")
async def deactivate_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Deactivate a prompt"""
    try:
        success = await PromptService.deactivate_prompt(db, prompt_id)
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return {"message": "Prompt deactivated successfully"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
