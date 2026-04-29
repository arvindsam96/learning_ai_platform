from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import Prompt, User
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse
from typing import List, Optional

class PromptService:
    @staticmethod
    async def create_prompt(db: AsyncSession, prompt_data: PromptCreate, user: User) -> PromptResponse:
        """Create a new prompt version"""
        # Get the latest version for this prompt name and type
        result = await db.execute(
            select(func.max(Prompt.version)).where(
                Prompt.name == prompt_data.name,
                Prompt.prompt_type == prompt_data.prompt_type
            )
        )
        latest_version = result.scalar() or 0
        
        prompt = Prompt(
            name=prompt_data.name,
            version=latest_version + 1,
            content=prompt_data.content,
            prompt_type=prompt_data.prompt_type,
            created_by=user.id
        )
        
        db.add(prompt)
        await db.commit()
        await db.refresh(prompt)
        
        return PromptResponse.model_validate(prompt)

    @staticmethod
    async def get_prompts(
        db: AsyncSession, 
        prompt_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[PromptResponse], int]:
        """Get prompts with optional filtering"""
        query = select(Prompt)
        
        if prompt_type:
            query = query.where(Prompt.prompt_type == prompt_type)
        if is_active is not None:
            query = query.where(Prompt.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(Prompt.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        prompts = result.scalars().all()
        
        return [PromptResponse.model_validate(p) for p in prompts], total

    @staticmethod
    async def get_prompt_by_id(db: AsyncSession, prompt_id: int) -> Optional[PromptResponse]:
        """Get a specific prompt by ID"""
        result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
        prompt = result.scalar_one_or_none()
        return PromptResponse.model_validate(prompt) if prompt else None

    @staticmethod
    async def get_active_prompt(
        db: AsyncSession, 
        name: str, 
        prompt_type: str
    ) -> Optional[PromptResponse]:
        """Get the active version of a prompt by name and type"""
        result = await db.execute(
            select(Prompt).where(
                Prompt.name == name,
                Prompt.prompt_type == prompt_type,
                Prompt.is_active == True
            ).order_by(Prompt.version.desc())
        )
        prompt = result.scalar_one_or_none()
        return PromptResponse.model_validate(prompt) if prompt else None

    @staticmethod
    async def update_prompt(
        db: AsyncSession, 
        prompt_id: int, 
        update_data: PromptUpdate,
        user: User
    ) -> Optional[PromptResponse]:
        """Update a prompt (creates new version)"""
        result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
        existing_prompt = result.scalar_one_or_none()
        
        if not existing_prompt:
            return None
        
        # Create new version
        new_prompt_data = PromptCreate(
            name=update_data.name or existing_prompt.name,
            content=update_data.content or existing_prompt.content,
            prompt_type=update_data.prompt_type or existing_prompt.prompt_type
        )
        
        return await PromptService.create_prompt(db, new_prompt_data, user)

    @staticmethod
    async def deactivate_prompt(db: AsyncSession, prompt_id: int) -> bool:
        """Deactivate a prompt"""
        result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
        prompt = result.scalar_one_or_none()
        
        if not prompt:
            return False
        
        prompt.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def activate_prompt(db: AsyncSession, prompt_id: int) -> bool:
        """Activate a prompt (deactivates other versions of same name/type)"""
        result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
        prompt = result.scalar_one_or_none()
        
        if not prompt:
            return False
        
        # Deactivate all other versions of this prompt
        await db.execute(
            select(Prompt).where(
                Prompt.name == prompt.name,
                Prompt.prompt_type == prompt.prompt_type,
                Prompt.id != prompt_id
            )
        )
        other_versions = result.scalars().all()
        for version in other_versions:
            version.is_active = False
        
        # Activate this version
        prompt.is_active = True
        await db.commit()
        return True
