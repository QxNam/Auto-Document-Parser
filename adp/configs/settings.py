from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Optional[str] = None
    DEBUG: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None

    # Pydantic configuration to load environment variables from a .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Singleton pattern
settings = Settings()
