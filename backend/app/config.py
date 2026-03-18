from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    gemini_api_key: str = ""
    groq_api_key: str = ""  # Free fallback when Gemini fails

    # CORS - Updated for Render deployment
    cors_origin: str = "http://localhost:3000"  # Will be overridden in production

    # Database
    db_path: str = "./sample.db"  # Keep for local development
    sample_csv_path: str = r"D:\gfg\7. Amazon Sales\Amazon Sales.csv"
    postgres_url: Optional[str] = None  # Required for production: postgresql://user:pass@host:5432/dbname

    # Production database flag
    use_postgres: bool = False  # Set to True in production

    # Supabase Authentication
    supabase_url: str = ""
    supabase_key: str = ""  # Service role key for backend
    supabase_jwt_secret: str = ""

    # Supabase Storage for file uploads
    supabase_storage_bucket: str = "csv-uploads"

    # JWT (for token generation/validation)
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # Render deployment settings
    port: int = 8000
    environment: str = "development"  # development, production

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
