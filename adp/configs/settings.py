from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Optional[str] = None

    DEBUG: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    S3_BUCKET_NAME_OUTPUT: Optional[str] = None

    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    SECRET_API_KEY: Optional[str] = None

    KAFKA_BOOTSTRAP_SERVERS: Optional[str] = "kafka:9092"
    KAFKA_TOPIC_NAME: Optional[str] = "upload"
    KAFKA_CONSUMER_GROUP_ID: Optional[str] = "adp-consumer-group"

    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    OBSERVER_TARGETS: Optional[list[str]] = ["local", "s3", "cache"]
    LOCAL_SAVED_DIR: Optional[str] = "/tmp/saved"
    API_TIMEOUT_INTERVAL: Optional[int] = 60
    MAX_FILE_SIZE_MB: Optional[int] = 10
    MAX_PAGE_COUNT: Optional[int] = 200
    ALLOWED_FILE_EXTENSIONS: Optional[str] = ".pdf,.docx,.txt"

    TESSDATA_PREFIX: Optional[str] = "./weights/tessdata"
    ARTIFACTS_PATH: Optional[str] = "./weights/models_docling"
    PAGE_BREAK_STR: Optional[str] = "\n--- Page break ---\n"

    GEMINI_API_KEY: Optional[str] = None
    OCR_ENGINE: str = "auto"  # Options: 'text_layer', 'ocr', 'auto'

    @field_validator("OBSERVER_TARGETS", mode="before")
    @classmethod
    def parse_observer_targets(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # Pydantic configuration to load environment variables from a .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Singleton pattern
settings = Settings()
