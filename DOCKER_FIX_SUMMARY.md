# Docker Connection Error - Fix Summary

## Problem
The application was failing to start with:
```
ConnectionRefusedError: [Errno 111] Connection refused
```

This occurred because:
1. The FastAPI app was trying to connect to PostgreSQL at `localhost:5432` during startup
2. When running in Docker, containers cannot reach `localhost` - they must use service names within the Docker network
3. The database URL was pointing to `localhost` but the database was running in a separate `db` container

## Solution Applied

### 1. **Created `.env.docker` File**
   - New environment file specifically for Docker deployments
   - Uses `db:5432` instead of `localhost:5432` for the database connection
   - Automatically used by `docker-compose.yml`

### 2. **Updated `docker-compose.yml`**
   - Changed `env_file: .env` to `env_file: .env.docker` for API and worker services
   - Added service health checks:
     - PostgreSQL health check using `pg_isready`
     - API health check using curl
   - Updated `depends_on` to use `condition: service_healthy` for database
   - This ensures the database is ready before the API tries to connect

### 3. **Enhanced `app/db/session.py`**
   - Added connection pool configuration:
     - `pool_size=5`: Maintains 5 connections
     - `max_overflow=10`: Allows up to 10 additional connections
   - Added timeouts: `timeout=10` and `command_timeout=10`
   - Added server settings for better compatibility

### 4. **Updated `app/core/config.py`**
   - Added fallback logic for `DATABASE_URL`
   - Detects Docker environment (checks `/.dockerenv` file)
   - Automatically adjusts database URL if running in Docker
   - Imports `os` module for environment detection

### 5. **Improved `app/main.py` Startup Logic**
   - Added retry mechanism for database connection
   - Retries up to 5 times with 2-second delays between attempts
   - Better error logging and informative messages
   - Gives the database time to start before giving up

### 6. **Updated `README.md`**
   - Added Docker deployment section explaining `.env` vs `.env.docker`
   - Added comprehensive Docker troubleshooting guide
   - Documented why `localhost` doesn't work in Docker
   - Provided recovery steps for common issues

## Files Modified
- ✅ `.env.docker` (new)
- ✅ `docker-compose.yml`
- ✅ `app/main.py`
- ✅ `app/core/config.py`
- ✅ `app/db/session.py`
- ✅ `README.md`

## Testing the Fix

### With Docker Compose
```bash
docker compose up --build
```

The application should now:
1. Wait for PostgreSQL to be healthy (5-second interval checks, 5 retries)
2. Connect successfully to the database
3. Create tables automatically
4. Start the API server on port 8000

Access the API at: http://localhost:8000

### Local Development
Use the existing `.env` file with `localhost:5432` and run:
```bash
uvicorn app.main:app --reload
```

## How It Works

When using Docker Compose:
1. Docker network created by compose has all services accessible by name
2. Inside the `api` container, `db` refers to the PostgreSQL container
3. The `.env.docker` file sets `DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/appdb`
4. Health checks ensure services start in the correct order
5. Retry logic handles timing issues during startup

When running locally:
1. PostgreSQL is accessed via `localhost`
2. The standard `.env` file is used with `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/appdb`
3. Manual startup of PostgreSQL is required: `brew services start postgresql`

