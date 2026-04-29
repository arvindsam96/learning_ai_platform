from fastapi import FastAPI
from app.core.config import settings
from app.db.session import create_tables
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.admin import router as admin_router
from app.api.v1.ai import router as ai_router
from app.api.v1.files import router as files_router
from app.api.v1.rag import router as rag_router
from app.api.v1.health import router as health_router
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
async def startup():
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            await create_tables()
            logger.info("Database tables created successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to create database tables after {max_retries} attempts")
                raise

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(files_router)
app.include_router(rag_router)
