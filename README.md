# Enterprise AI Platform

A production-grade FastAPI backend platform designed for AI-powered applications with comprehensive features including user authentication, multi-provider LLM routing, document indexing, RAG (Retrieval-Augmented Generation), and async job processing.

## 🚀 Features

### Core Architecture
- **Async FastAPI**: High-performance async REST API with full OpenAPI/Swagger documentation
- **PostgreSQL + AsyncPG**: Asynchronous database with SQLAlchemy 2.0 ORM
- **Redis**: Caching and session management
- **JWT + RBAC**: Secure authentication with role-based access control
- **Celery Workers**: Background job processing for document indexing and async tasks
- **Alembic**: Database migrations (production-ready)

### AI & LLM Features
- **Multi-Provider LLM Support**: Seamless integration with:
  - OpenAI (GPT-4, GPT-4o, etc.)
  - Anthropic (Claude 3.5, etc.)
  - Google Generative AI (Gemini)
  - Ollama (local models)
- **Provider Fallback**: Automatic failover between providers if one fails
- **Flexible Model Selection**: Choose provider and model per request
- **Usage Logging**: Track all LLM calls with latency and token usage metrics

### Document & RAG Features
- **File Upload & Indexing**: Support for PDF, DOCX, and other document formats
- **Intelligent Chunking**: Automatic document splitting into searchable chunks
- **Pinecone Integration**: Vector embeddings and semantic search with Pinecone
- **OpenAI Embeddings**: High-quality text embeddings for RAG
- **RAG Query**: Query documents using natural language with LLM-augmented responses

### User Management
- **User Registration & Authentication**: Email-based user registration with secure password hashing
- **Token Management**: Access tokens and refresh tokens with configurable expiration
- **Role-Based Access**: User and admin roles for authorization
- **User Profiles**: Track user metadata and activity

### Monitoring & Analytics
- **Usage Logs**: Comprehensive logging of all AI/LLM operations
- **Admin Dashboard**: Monitor platform usage and health
- **Health Checks**: Ready endpoint for monitoring

### AWS Cloud Features
- **S3 File Storage**: Scalable file storage with automatic fallback to local storage
- **ECS/EKS Deployment**: Containerized deployment on AWS ECS Fargate or EKS
- **Terraform Infrastructure**: Complete infrastructure as code for AWS resources
- **AWS Secrets Manager**: Secure secret management for API keys and sensitive data
- **Prompt Versioning**: Database-backed prompt management with versioning
- **CI/CD Pipeline**: GitHub Actions for automated testing, building, and deployment
- **CloudWatch Monitoring**: Comprehensive dashboards and alerts for all services
- **Auto Scaling**: ECS service scaling based on CPU, memory, and request metrics
- **CloudFront CDN**: Global content delivery network for improved performance
- **Automated Backups**: RDS automated backups with enhanced monitoring

## 📊 Architecture Diagrams

### High-Level Design (HLD)

```mermaid
graph TD
    A[User/Client] --> B[FastAPI API Server]
    B --> C[Authentication & User Management]
    B --> D[AI Chat Service]
    B --> E[File Upload & Management]
    B --> F[RAG Query Service]
    B --> G[Admin Dashboard]
    D --> H[LLM Providers]
    H --> I[OpenAI]
    H --> J[Anthropic]
    H --> K[Google Gemini]
    H --> L[Ollama]
    E --> M[S3 File Storage]
    F --> N[Pinecone Vector Database]
    C --> O[PostgreSQL Database]
    D --> O
    E --> O
    F --> O
    B --> P[Redis Cache]
    Q[Celery Workers] --> O
    Q --> N
    Q --> M
    Q --> R[Usage Logging]
    R --> O
```

### Low-Level Design (LLD)

#### AI Service Class Diagram

```mermaid
classDiagram
    class AIService {
        +chat(request: ChatRequest)
        -_get_provider(provider: str)
    }
    class ProviderFactory {
        +get_provider(provider_name: str)
    }
    class BaseProvider {
        <<interface>>
        +chat(messages: list)
        +get_model()
    }
    class OpenAIProvider {
        +chat(messages: list)
        -client: OpenAI
    }
    class AnthropicProvider {
        +chat(messages: list)
        -client: Anthropic
    }
    class GeminiProvider {
        +chat(messages: list)
        -client: GenerativeModel
    }
    class OllamaProvider {
        +chat(messages: list)
        -client: Client
    }
    AIService --> ProviderFactory
    ProviderFactory --> BaseProvider
    BaseProvider <|-- OpenAIProvider
    BaseProvider <|-- AnthropicProvider
    BaseProvider <|-- GeminiProvider
    BaseProvider <|-- OllamaProvider
```

#### RAG Service Class Diagram

```mermaid
classDiagram
    class RAGService {
        +query(request: RAGQueryRequest)
        -_embed_query(query: str)
        -_search_vectors(embedding)
        -_generate_response(query, context)
    }
    class EmbeddingsService {
        +generate_embedding(text: str)
    }
    class PineconeClient {
        +upsert(vectors)
        +query(embedding)
    }
    class Chunker {
        +chunk_document(document: str)
    }
    class Parser {
        +parse_file(file)
    }
    RAGService --> EmbeddingsService
    RAGService --> PineconeClient
    RAGService --> AIService
    Chunker --> Parser
```

### API Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant AuthService
    participant AIService
    participant Provider
    participant DB
    participant Redis

    Client->>FastAPI: POST /ai/chat (with Bearer Token)
    FastAPI->>AuthService: Verify JWT Token
    AuthService-->>FastAPI: User authenticated
    FastAPI->>Redis: Check cache (optional)
    Redis-->>FastAPI: Cache miss
    FastAPI->>AIService: chat(request)
    AIService->>Provider: chat(messages)
    Provider-->>AIService: LLM response
    AIService-->>FastAPI: Formatted response
    FastAPI->>DB: Log usage (provider, tokens, latency)
    FastAPI->>Redis: Cache response (optional)
    FastAPI-->>Client: JSON response

    Note over Client,FastAPI: For RAG Query
    Client->>FastAPI: POST /rag/query
    FastAPI->>AuthService: Verify JWT
    AuthService-->>FastAPI: OK
    FastAPI->>RAGService: query(request)
    RAGService->>EmbeddingsService: generate_embedding(query)
    EmbeddingsService-->>RAGService: embedding
    RAGService->>PineconeClient: query(embedding)
    PineconeClient-->>RAGService: relevant chunks
    RAGService->>AIService: generate_response(query, context)
    AIService-->>RAGService: augmented response
    RAGService-->>FastAPI: response
    FastAPI->>DB: Log usage
    FastAPI-->>Client: response
```

## 📋 Requirements

- Python 3.13+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (for containerized setup)

## 🔧 Installation & Setup

### Quick Start (Docker)

```bash
cp .env.example .env
# Update API keys in .env as needed
docker compose up --build
```

Access Swagger UI: http://localhost:8000/docs

### Local Development (without Docker)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL and Redis:**
   ```bash
   brew services start postgresql
   brew services start redis
   ```

3. **Create database:**
   ```bash
   createdb appdb
   ```

4. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 API Endpoints

### Authentication (`/auth`)
| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/auth/register` | None |
| POST | `/auth/login` | None |
| POST | `/auth/refresh` | Refresh Token |
| POST | `/auth/logout` | Bearer Token |

### User Management (`/users`)
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/users/me` | Bearer Token |

### Administration (`/admin`)
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/admin/dashboard` | Bearer Token + Admin |

### AI Chat (`/ai`)
| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/ai/chat` | Bearer Token |

### Document Management (`/files`)
| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/files/upload` | Bearer Token |
| GET | `/files` | Bearer Token |
| DELETE | `/files/{document_id}` | Bearer Token |

### RAG Query (`/rag`)
| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/rag/query` | Bearer Token |

### Health Check (`/health`)
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/health` | None |

## 🏗️ Project Structure

```
learning_ai_platform/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── api/v1/              # API routes
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management
│   │   ├── admin.py         # Admin operations
│   │   ├── ai.py            # LLM chat endpoints
│   │   ├── files.py         # Document management
│   │   ├── rag.py           # RAG query endpoints
│   │   ├── health.py        # Health check
│   ├── ai/                  # AI/LLM service layer
│   │   ├── service.py       # Chat orchestration
│   │   └── providers/       # LLM provider implementations
│   ├── rag/                 # RAG/Document indexing
│   │   ├── service.py       # RAG orchestration
│   │   ├── chunker.py       # Document chunking
│   │   ├── parser.py        # Document parsing
│   │   ├── embeddings.py    # Embedding generation
│   │   └── pinecone_client.py
│   ├── core/                # Core configurations
│   │   ├── config.py        # Pydantic settings
│   │   ├── security.py      # JWT & password utilities
│   │   ├── deps.py          # Dependency injection
│   │   └── redis.py         # Redis client
│   ├── db/                  # Database & ORM
│   │   ├── base.py          # SQLAlchemy base
│   │   ├── models.py        # Data models
│   │   └── session.py       # Database session management
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── ai.py
│   │   └── rag.py
│   └── workers/             # Celery background tasks
│       └── tasks.py
├── docker-compose.yml       # Multi-container orchestration
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## 🔐 Environment Configuration

Required environment variables:

| Variable | Type | Description |
|----------|------|-------------|
| `DATABASE_URL` | Required | PostgreSQL connection string |
| `REDIS_URL` | Required | Redis connection string |
| `SECRET_KEY` | Required | JWT signing key (min 32 chars) |
| `OPENAI_API_KEY` | Optional | OpenAI API key |
| `ANTHROPIC_API_KEY` | Optional | Anthropic API key |
| `GEMINI_API_KEY` | Optional | Google Generative AI API key |
| `PINECONE_API_KEY` | Optional | Pinecone API key |
| `DEFAULT_PROVIDER` | Optional | Default LLM provider (default: openai) |
| `DEFAULT_MODEL` | Optional | Default LLM model (default: gpt-4o-mini) |

## 🚢 Docker Deployment

### Quick Start
```bash
docker compose up --build
```

Services:
- **API**: FastAPI server (port 8000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache (port 6379)
- **Celery Worker**: Background tasks

### Environment Configuration

The project uses different `.env` files for different environments:

- `.env`: Local development (uses `localhost:5432` for database)
- `.env.docker`: Docker environment (uses `db:5432` for database)

When running with Docker Compose, the `.env.docker` file is automatically used.

## 📖 Database Models

### User
- Unique email and secure password hashing
- Role-based access (user/admin)
- Refresh token management

### Document
- Associated with user
- Tracks indexing status and chunk count
- Stores file metadata

### UsageLog
- Logs all LLM API calls
- Tracks provider, model, latency, and token usage
- Useful for analytics and monitoring

## 🛠️ Troubleshooting

### Docker Issues

#### "Connection refused" when running `docker compose up`
This occurs when the API container tries to connect to the database before it's ready.

**Solution**: The application now includes automatic retry logic with exponential backoff. The database connection is retried up to 5 times with 2-second delays.

**To manually verify**:
```bash
# Check if all services are running
docker compose ps

# Check logs for specific service
docker compose logs api
docker compose logs db

# Restart services
docker compose down
docker compose up --build
```

#### Database won't start
```bash
# Reset the Docker volumes and start fresh
docker compose down -v
docker compose up --build
```

#### API cannot connect to PostgreSQL in Docker
Ensure you're using `.env.docker` when running with Docker Compose. The key difference is:
- `.env` (local): `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/appdb`
- `.env.docker` (Docker): `DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/appdb`

Note: Use `db` instead of `localhost` when running in Docker, as containers communicate through service names.

### PostgreSQL Connection Issues (Local Development)
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql
```

### Redis Connection Issues
```bash
# Check if Redis is running
brew services list | grep redis

# Start Redis
brew services start redis
```

### LLM Provider Errors
- Verify API keys in `.env`
- Platform automatically falls back to other providers
- Check provider credentials are valid

## 📝 Production Notes

- Tables are auto-created on startup (development mode)
- For production, use Alembic migrations
- Generate strong `SECRET_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Use managed databases (RDS, Cloud SQL)
- Use managed Redis (ElastiCache, Redis Cloud)

## 📦 Dependencies

Key packages:
- FastAPI 0.115.6
- SQLAlchemy 2.0.36
- Pydantic 2.10.4
- OpenAI 1.58.1
- Anthropic 0.42.0
- Pinecone 5.0.1
- Tavily 0.5.0
- Celery 5.4.0

See `requirements.txt` for full list.

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows PEP 8
- Tests pass: `pytest`
- Type hints included
- Docstrings provided

## 📄 License

Enterprise AI Platform
