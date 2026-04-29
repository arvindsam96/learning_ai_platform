from pathlib import Path
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile
from app.core.config import settings
from app.db.models import Document, User
from app.rag.parser import parse_file
from app.rag.chunker import chunk_text
from app.rag.embeddings import EmbeddingService
from app.rag.pinecone_client import PineconeStore
from app.ai.service import run_chat
from app.rag.tavily_client import TavilySearch
from app.core.s3_client import S3Client
from app.ai.prompt_service import PromptService

SUPPORTED_EXT = {".pdf", ".docx", ".txt", ".md", ".csv"}

def namespace_for_user(user_id: int) -> str:
    return f"user_{user_id}"

async def save_upload(file: UploadFile, user: User) -> str:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXT:
        raise ValueError(f"Unsupported file extension: {suffix}")
    
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError("File too large")
    
    safe_name = f"{uuid4().hex}{suffix}"
    
    # Try S3 first if configured, otherwise use local storage
    s3_client = S3Client()
    if s3_client.is_available():
        try:
            s3_key = f"uploads/{user.id}/{safe_name}"
            s3_url = await s3_client.upload_file(content, s3_key, file.content_type)
            return s3_url
        except Exception:
            # Fallback to local storage if S3 fails
            pass
    
    # Local storage fallback
    upload_dir = Path(settings.UPLOAD_DIR) / str(user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / safe_name
    dest.write_bytes(content)
    return str(dest)

async def index_document(db: AsyncSession, user: User, file: UploadFile) -> Document:
    storage_path = await save_upload(file, user)
    doc = Document(user_id=user.id, filename=file.filename or Path(storage_path).name, storage_path=storage_path, status="processing")
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    try:
        text = await parse_file(storage_path)
        chunks = chunk_text(text)
        embeddings = await EmbeddingService().embed_documents(chunks)
        vectors = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            vectors.append({
                "id": f"doc_{doc.id}_chunk_{i}",
                "values": emb,
                "metadata": {"document_id": doc.id, "chunk_index": i, "filename": doc.filename, "text": chunk[:3500]},
            })
        if vectors:
            PineconeStore().upsert(vectors, namespace_for_user(user.id))
        doc.status = "indexed"
        doc.chunk_count = len(chunks)
        await db.commit()
        await db.refresh(doc)
        return doc
    except Exception:
        doc.status = "failed"
        await db.commit()
        raise

async def query_rag(db: AsyncSession, user: User, question: str, provider: str | None, model: str | None, top_k: int = 5, include_web_search: bool = False) -> dict:
    q_vector = await EmbeddingService().embed_text(question)
    results = PineconeStore().query(q_vector, namespace_for_user(user.id), top_k=top_k)
    matches = getattr(results, "matches", []) or results.get("matches", [])
    sources = []
    context_parts = []
    for match in matches:
        meta = getattr(match, "metadata", None) or match.get("metadata", {})
        score = getattr(match, "score", None) or match.get("score")
        text = meta.get("text", "")
        context_parts.append(f"Source: {meta.get('filename')}\n{text}")
        sources.append({"filename": meta.get("filename"), "document_id": meta.get("document_id"), "chunk_index": meta.get("chunk_index"), "score": score})
    
    if include_web_search:
        tavily = TavilySearch()
        web_results = await tavily.search(question, max_results=3)
        for result in web_results:
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")
            context_parts.append(f"Web Source: {title} ({url})\n{content}")
            sources.append({"title": title, "url": url, "content": content[:500], "type": "web"})
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Get active RAG system prompt from database
    rag_prompt = await PromptService.get_active_prompt(db, "rag_system", "system")
    system_prompt = rag_prompt.content if rag_prompt else "Answer using the provided context. If the answer is not in context, use your general knowledge but note that it's not from the provided sources."
    
    if not include_web_search:
        # Get default RAG prompt for document-only queries
        default_rag_prompt = await PromptService.get_active_prompt(db, "rag_system_default", "system")
        system_prompt = default_rag_prompt.content if default_rag_prompt else "Answer using only the provided context. If the answer is not in context, say you do not know based on the uploaded documents."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    answer = await run_chat(db, user, provider, model, messages)
    return {"answer": answer["response"], "sources": sources, "provider": answer["provider"], "model": answer["model"]}

async def list_documents(db: AsyncSession, user: User) -> list[Document]:
    result = await db.execute(select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc()))
    return list(result.scalars().all())

async def delete_document(db: AsyncSession, user: User, document_id: int) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id, Document.user_id == user.id))
    doc = result.scalar_one_or_none()
    if not doc:
        return
    try:
        PineconeStore().delete_by_filter(namespace_for_user(user.id), doc.id)
    except Exception:
        pass
    try:
        Path(doc.storage_path).unlink(missing_ok=True)
    except Exception:
        pass
    await db.delete(doc)
    await db.commit()
