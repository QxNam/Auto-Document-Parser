import os
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from adp.configs.logger import get_logger
from adp.configs.settings import settings

logger = get_logger(__name__)


class S3Service:
    def __init__(self):
        s3_config = Config(
            region_name=settings.AWS_DEFAULT_REGION,
            retries={"max_attempts": 3, "mode": "standard"},
            max_pool_connections=20,
        )

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
            config=s3_config,
        )
        self.bucket_name = getattr(settings, "S3_BUCKET_NAME", None)

    def upload_file(self, local_path: str, s3_key: str, bucket: Optional[str] = None) -> bool:
        """Tải file từ máy cục bộ lên S3."""
        target_bucket = bucket or self.bucket_name

        if not os.path.exists(local_path):
            logger.error(f"Local file not found: {local_path}")
            return False

        try:
            self.s3_client.upload_file(local_path, target_bucket, s3_key)
            logger.info(f"Successfully uploaded {local_path} to s3://{target_bucket}/{s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False

    def delete_file(self, s3_key: str, bucket: Optional[str] = None) -> bool:
        """Xóa một file trên S3."""
        target_bucket = bucket or self.bucket_name
        try:
            self.s3_client.delete_object(Bucket=target_bucket, Key=s3_key)
            logger.info(f"Successfully deleted s3://{target_bucket}/{s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {s3_key}: {e}")
            return False

    def get_uri(self, s3_key: str, bucket: Optional[str] = None) -> str:
        """Trả về URI chuẩn (s3://bucket/key) của file."""
        target_bucket = bucket or self.bucket_name
        return f"s3://{target_bucket}/{s3_key}"

    def get_presigned_url(self, s3_key: str, expiration: int = 3600, bucket: Optional[str] = None) -> Optional[str]:
        """Tạo URL tạm thời để UI có thể tải/xem file (ví dụ: file PDF/Image)."""
        target_bucket = bucket or self.bucket_name
        try:
            response = self.s3_client.generate_presigned_url(
                "get_object", Params={"Bucket": target_bucket, "Key": s3_key}, ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None
