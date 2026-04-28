from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.db.models import User
from app.rag.service import index_document, list_documents, delete_document

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        doc = await index_document(db, user, file)
        return {"id": doc.id, "filename": doc.filename, "status": doc.status, "chunks": doc.chunk_count}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("")
async def files(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    docs = await list_documents(db, user)
    return [{"id": d.id, "filename": d.filename, "status": d.status, "chunks": d.chunk_count, "created_at": d.created_at} for d in docs]

@router.delete("/{document_id}")
async def remove_file(document_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await delete_document(db, user, document_id)
    return {"message": "deleted"}
