from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pydantic import validator
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    # API keys
    OPENAI_API_KEY: str

    # Database configuration
    DATABASE_URL: str

    # CORS configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Application metadata
    APP_NAME: str = "Argument Map API"
    APP_VERSION: str = "0.1.0"

    # Validator to parse comma-separated ALLOWED_ORIGINS from .env
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, value):
        if isinstance(value, str):
            # Split comma-separated string into a list, strip whitespace
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    # Pydantic-settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra env vars not defined in the model
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Cached retrieval of settings to avoid repeated loading.
    """
    return Settings()

# Instantiate settings for use throughout the application
settings = get_settings()