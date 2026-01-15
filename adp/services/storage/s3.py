from urllib.parse import urlparse
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Dict

from adp.configs.settings import settings
from adp.configs.logger import get_logger

logger = get_logger(__name__)

class S3Service:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(S3Service, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        s3_config = Config(
            region_name=settings.AWS_DEFAULT_REGION,
            retries={'max_attempts': 3, 'mode': 'standard'},
            max_pool_connections=20
        )

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=s3_config
        )
        self.bucket_name = getattr(settings, 'S3_BUCKET_NAME', None)
        self._initialized = True
        logger.info("✅ S3Service Singleton initialized with Connection Pooling.")

    def upload_fileobj(
        self, file_obj, bucket_name: str, object_key: str, extra_args: Dict = None
    ) -> dict:
        """Upload a file-like object to S3."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")
            
            self.s3_client.upload_fileobj(
                file_obj, bucket_name, object_key, ExtraArgs=extra_args or {}
            )

            logger.info(f"✅ S3 fileobj uploaded to s3://{bucket_name}/{object_key}")
            return {
                "status": True, 
                "uri": f"s3://{bucket_name}/{object_key}"
            }

        except ClientError as e:
            raise RuntimeError(f"S3 fileobj upload error: {e}") from e

    def get_s3_uri(self, bucket_name: str, object_key: str) -> str:
        """Return the S3 URI for the given bucket and object key."""
        return f"s3://{bucket_name}/{object_key}"
        
    def validate_s3_uri(uri: str) -> tuple[str, str]:
        """
        Validate and parse an S3 URI into bucket and key.
        """
        p = urlparse(uri)
        if p.scheme != "s3" or not p.netloc or not p.path:
            raise ValueError(f"Invalid s3 uri: {uri}")
        bucket = p.netloc
        key = p.path.lstrip("/")
        return bucket, key

    def download_fileobj(
        self, bucket_name: str, object_key: str, file_obj
    ) -> None:
        """Download a file-like object from S3."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")
            
            self.s3_client.download_fileobj(
                bucket_name, object_key, file_obj
            )
            logger.info(f"✅ S3 fileobj downloaded from s3://{bucket_name}/{object_key}")

        except ClientError as e:
            raise RuntimeError(f"S3 fileobj download error: {e}") from e
        
    def delete_object(self, bucket_name: str, object_key: str) -> None:
        """Delete an object from S3."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")
            
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            logger.info(f"✅ S3 object deleted from s3://{bucket_name}/{object_key}")

        except ClientError as e:
            raise RuntimeError(f"S3 delete object error: {e}") from e
        
s3_service = S3Service()
        