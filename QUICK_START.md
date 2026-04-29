# Quick Start Guide - Docker

## The Fix
Your application was failing because it couldn't connect to PostgreSQL. This has been fixed!

## Running the Application

### Option 1: Docker Compose (Recommended)
```bash
cd /Users/apple/Documents/Projects/learning_ai_platform
docker compose up --build
```

The application will:
1. Wait for PostgreSQL to start (with health checks)
2. Create database tables automatically  
3. Start the API on http://localhost:8000
4. Start background workers for async tasks

**First time setup may take 1-2 minutes** as Docker builds images and PostgreSQL initializes.

### Option 2: Local Development
```bash
# Start PostgreSQL
brew services start postgresql

# Start Redis
brew services start redis

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload
```

## Testing
Once running, visit: http://localhost:8000/docs

This opens the Swagger UI where you can test all endpoints.

## Troubleshooting

### Still getting "Connection refused"?
```bash
# Check if services are running
docker compose ps

# See detailed logs
docker compose logs api

# Reset everything and start fresh
docker compose down -v
docker compose up --build
```

### Database won't initialize
```bash
# Remove Docker volumes and rebuild
docker compose down -v
docker volume rm learning_ai_platform_postgres_data
docker compose up --build
```

## Key Changes Made

The issue was that:
- Local development uses `localhost:5432`
- Docker containers need to use `db:5432` (service name)

**Solution**: Created `.env.docker` with correct database URL and updated health checks.

## Environment Variables

### `.env` (Local Development)
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/appdb
```

### `.env.docker` (Docker)
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/appdb
```

## What Was Fixed

1. ✅ Separate environment files for local vs Docker
2. ✅ Docker health checks to ensure proper startup order
3. ✅ Retry logic with exponential backoff (5 attempts)
4. ✅ Better connection pooling configuration
5. ✅ Improved error messages and logging
6. ✅ Updated documentation

## Next Steps

- Configure API keys in `.env.docker` for OpenAI, Anthropic, etc.
- Read the main README.md for full API documentation
- Check the health endpoint: http://localhost:8000/health

