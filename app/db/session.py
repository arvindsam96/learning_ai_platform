from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def create_tables() -> None:
    from app.db.base import Base
    from app.db import models  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
