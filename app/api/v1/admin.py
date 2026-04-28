from fastapi import APIRouter, Depends
from app.core.deps import require_role
from app.db.models import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard")
async def dashboard(user: User = Depends(require_role("admin"))):
    return {"message": "Welcome admin", "email": user.email}
