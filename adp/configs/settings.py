from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MODE: Optional[str] = None

    DEBUG: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None

    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_DB: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    SECRET_API_KEY: Optional[str] = None

    KAFKA_BOOTSTRAP_SERVERS: Optional[str] = "kafka:9092"
    KAFKA_TOPIC_UPLOADS: Optional[str] = "document-uploads"
    KAFKA_CONSUMER_GROUP_ID: Optional[str] = "adp-consumer-group"

    API_TIMEOUT_INTERVAL: Optional[int] = 60
    MAX_FILE_SIZE_MB: Optional[int] = 10
    ALLOWED_FILE_EXTENSIONS: Optional[str] = ".pdf,.docx,.txt"

    # Pydantic configuration to load environment variables from a .env file
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Singleton pattern
settings = Settings()
