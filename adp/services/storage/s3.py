"""
S3 Storage Service với Prometheus Metrics

Service này quản lý S3 operations và track metrics về:
- Thời gian upload/download/delete
- Số operations thành công/thất bại
- Kích thước file upload
- Lỗi S3
"""

import os
import time
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from adp.configs.logger import get_logger
from adp.configs.settings import settings

# Import metrics
from adp.monitoring import (
    s3_operation_duration_seconds,
    s3_operations_total,
    s3_upload_size_bytes,
    s3_errors_total,
)

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
        """
        Tải file từ máy cục bộ lên S3 và track metrics.
        
        Metrics tracked:
        - Thời gian upload (histogram)
        - Số operations (counter)
        - Kích thước file (histogram)
        - Lỗi S3 (counter)
        """
        target_bucket = bucket or self.bucket_name
        operation = "upload"
        
        # Kiểm tra file tồn tại
        if not os.path.exists(local_path):
            logger.error(f"Local file not found: {local_path}")
            
            # ❌ TRACK METRICS - FILE NOT FOUND
            s3_operations_total.labels(
                bucket=target_bucket,
                operation=operation,
                status="failed"
            ).inc()
            
            s3_errors_total.labels(
                bucket=target_bucket,
                operation=operation,
                error_type="FileNotFound"
            ).inc()
            
            return False

        # Lấy file size
        file_size = os.path.getsize(local_path)
        
        # Bắt đầu đếm thời gian
        start_time = time.time()
        
        try:
            # Upload file lên S3
            self.s3_client.upload_file(local_path, target_bucket, s3_key)
            
            # Tính thời gian upload
            duration = time.time() - start_time
            
            # ✅ TRACK METRICS - THÀNH CÔNG
            # 1. Ghi nhận thời gian upload
            s3_operation_duration_seconds.labels(
                bucket=target_bucket,
                operation=operation
            ).observe(duration)
            
            # 2. Tăng counter upload thành công
            s3_operations_total.labels(
                bucket=target_bucket,
                operation=operation,
                status="success"
            ).inc()
            
            # 3. Ghi nhận file size
            s3_upload_size_bytes.labels(
                bucket=target_bucket
            ).observe(file_size)
            
            logger.info(f"Successfully uploaded {local_path} to s3://{target_bucket}/{s3_key} in {duration:.2f}s")
            return True
            
        except ClientError as e:
            # ❌ TRACK METRICS - CLIENT ERROR
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            s3_operations_total.labels(
                bucket=target_bucket,
                operation=operation,
                status="failed"
            ).inc()
            
            s3_errors_total.labels(
                bucket=target_bucket,
                operation=operation,
                error_type=error_code
            ).inc()
            
            logger.error(f"Failed to upload {local_path}: {e}")
            return False

    def delete_file(self, s3_key: str, bucket: Optional[str] = None) -> bool:
        """
        Xóa một file trên S3 và track metrics.
        """
        target_bucket = bucket or self.bucket_name
        operation = "delete"
        
        # Bắt đầu đếm thời gian
        start_time = time.time()
        
        try:
            # Delete file từ S3
            self.s3_client.delete_object(Bucket=target_bucket, Key=s3_key)
            
            # Tính thời gian delete
            duration = time.time() - start_time
            
            # ✅ TRACK METRICS - THÀNH CÔNG
            s3_operation_duration_seconds.labels(
                bucket=target_bucket,
                operation=operation
            ).observe(duration)
            
            s3_operations_total.labels(
                bucket=target_bucket,
                operation=operation,
                status="success"
            ).inc()
            
            logger.info(f"Successfully deleted s3://{target_bucket}/{s3_key} in {duration:.2f}s")
            return True
            
        except ClientError as e:
            # ❌ TRACK METRICS - CLIENT ERROR
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            s3_operations_total.labels(
                bucket=target_bucket,
                operation=operation,
                status="failed"
            ).inc()
            
            s3_errors_total.labels(
                bucket=target_bucket,
                operation=operation,
                error_type=error_code
            ).inc()
            
            logger.error(f"Failed to delete {s3_key}: {e}")
            return False

    def get_uri(self, s3_key: str, bucket: Optional[str] = None) -> str:
        """Trả về URI chuẩn (s3://bucket/key) của file."""
        target_bucket = bucket or self.bucket_name
        return f"s3://{target_bucket}/{s3_key}"

    def get_presigned_url(self, s3_key: str, expiration: int = 3600, bucket: Optional[str] = None) -> Optional[str]:
        """
        Tạo URL tạm thời để UI có thể tải/xem file và track metrics.
        """
        target_bucket = bucket or self.bucket_name
        operation = "get_presigned_url"
        
        # Bắt đầu đếm thời gian
        start_time = time.time()
        
        try:
            # Generate presigned URL
            response = self.s3_client.generate_presigned_url(
                "get_object", Params={"Bucket": target_bucket, "Key": s3_key}, ExpiresIn=expiration
            )
            
            # Tính thời gian
            duration = time.time() - start_time
            
            # ✅ TRACK METRICS - THÀNH CÔNG
            s3_operation_duration_seconds.labels(
                bucket=target_bucket,
                operation=operation
            ).observe(duration)
            
            s3_operations_total.labels(
                bucket=target_bucket,
                operation=operation,
                status="success"
            ).inc()
            
            return response
            
        except ClientError as e:
            # ❌ TRACK METRICS - CLIENT ERROR
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            s3_operations_total.labels(
                bucket=target_bucket,
                operation=operation,
                status="failed"
            ).inc()
            
            s3_errors_total.labels(
                bucket=target_bucket,
                operation=operation,
                error_type=error_code
            ).inc()
            
            logger.error(f"Error generating presigned URL: {e}")
            return None

