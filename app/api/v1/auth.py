from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials
from app.core.deps import get_db, get_current_user, security
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.redis import redis_client
from app.db.models import User
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.schemas.auth import TokenResponse, RefreshRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(email=data.email, hashed_password=hash_password(data.password), role="user")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(user.email, user.role, user.id)
    refresh = create_refresh_token(user.email, user.id)
    user.refresh_token = refresh
    await db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    result = await db.execute(select(User).where(User.id == payload.get("uid")))
    user = result.scalar_one_or_none()
    if not user or user.refresh_token != data.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return TokenResponse(access_token=create_access_token(user.email, user.role, user.id))

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), user: User = Depends(get_current_user)):
    token = credentials.credentials
    redis_client.setex(f"blacklist:{token}", 60 * 60 * 24, "1")
    return {"message": "Logged out"}
