# Enterprise AI Platform

Production-style FastAPI backend with async PostgreSQL, Redis, JWT/RBAC, multi-provider LLM routing, Pinecone RAG, Docker, and worker scaffold.

## Run

```bash
cp .env.example .env
# fill API keys where needed
docker compose up --build
```

Open Swagger: http://localhost:8000/docs

## Main APIs

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /users/me`
- `GET /admin/dashboard`
- `POST /ai/chat`
- `POST /files/upload`
- `GET /files`
- `DELETE /files/{document_id}`
- `POST /rag/query`

## Notes

For local demos, tables are created on app startup. For production, use Alembic migrations and managed secrets.
