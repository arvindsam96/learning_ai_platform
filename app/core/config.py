from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    APP_NAME: str = "Enterprise AI Platform"
    ENV: str = "local"
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    DEFAULT_PROVIDER: str = "openai"
    DEFAULT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "enterprise-ai-platform"
    PINECONE_DIMENSION: int = 1536
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_MB: int = 25

settings = Settings()
