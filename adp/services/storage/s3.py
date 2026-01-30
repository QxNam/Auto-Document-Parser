import io
import os
from typing import Dict
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from adp.configs.logger import api_logger, worker_logger
from adp.configs.settings import settings


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
            retries={"max_attempts": 3, "mode": "standard"},
            max_pool_connections=20,
        )

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=s3_config,
        )
        self.bucket_name = getattr(settings, "S3_BUCKET_NAME", None)
        self._initialized = True
        worker_logger.info("✅ S3Service Singleton initialized with Connection Pooling.")
        api_logger.info("✅ S3Service Singleton initialized with Connection Pooling.")

    def upload_fileobj(self, file_obj, bucket_name: str, object_key: str, extra_args: Dict = None) -> dict:
        """Upload a file-like object to S3."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")

            self.s3_client.upload_fileobj(file_obj, bucket_name, object_key, ExtraArgs=extra_args or {})

            # logger.info(f"✅ S3 fileobj uploaded to s3://{bucket_name}/{object_key}")
            return {"status": True, "uri": f"s3://{bucket_name}/{object_key}"}

        except ClientError as e:
            raise RuntimeError(f"S3 fileobj upload error: {e}") from e

    def get_s3_uri(self, bucket_name: str, object_key: str) -> str:
        """Return the S3 URI for the given bucket and object key."""
        return f"s3://{bucket_name}/{object_key}"

    def parse_s3_uri(self, uri: str) -> tuple[str, str]:
        """
        Parse an S3 URI into bucket and key.
        """
        p = urlparse(uri)
        if p.scheme != "s3" or not p.netloc or not p.path:
            raise ValueError(f"Invalid s3 uri: {uri}")
        bucket = p.netloc
        key = p.path.lstrip("/")
        return bucket, key

    def download_fileobj(self, bucket_name: str, object_key: str) -> io.BytesIO:
        """Download a file-like object from S3."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")

            file_buffer = io.BytesIO()
            self.s3_client.download_fileobj(bucket_name, object_key, file_buffer)
            file_buffer.seek(0)

            # logger.info(f"✅ S3 fileobj downloaded from s3://{bucket_name}/{object_key}")
            return file_buffer

        except ClientError as e:
            raise RuntimeError(f"S3 fileobj download error: {e}") from e

    def download_file(self, bucket_name: str, key: str, output_path: str) -> str:
        """
        Download a file from S3 to a local path and return path.
        """
        try:
            directory = os.path.dirname(output_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                # logger.info(f"📁 Created: {directory}")

            # logger.info(f"📥 Downloading: s3://{bucket_name}/{key} -> {output_path}")

            target_bucket = bucket_name or self.bucket_name
            if not target_bucket:
                raise ValueError("Bucket name must not be empty.")

            self.s3_client.download_file(target_bucket, key, output_path)

            # logger.info(f"✅ File downloaded successfully.")
            return output_path

        except ClientError as e:
            raise RuntimeError(f"S3 fileobj download error: {e}") from e

    def delete_object(self, bucket_name: str, object_key: str) -> None:
        """Delete an object from S3."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")

            self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            # logger.info(f"✅ S3 object deleted from s3://{bucket_name}/{object_key}")

        except ClientError as e:
            raise RuntimeError(f"S3 delete object error: {e}") from e

    def delete_all_objects(self, bucket_name: str, prefix: str = "") -> None:
        """Delete all objects in an S3 bucket with the given prefix."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")

            paginator = self.s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

            objects_to_delete = []
            for page in page_iterator:
                contents = page.get("Contents", [])
                for obj in contents:
                    objects_to_delete.append({"Key": obj["Key"]})

            if objects_to_delete:
                self.s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": objects_to_delete})
                # logger.info(f"✅ Deleted all objects in s3://{bucket_name}/{prefix}")
            else:
                # logger.info(f"ℹ️ No objects found to delete in s3://{bucket_name}/{prefix}")
                pass

        except ClientError as e:
            raise RuntimeError(f"S3 delete all objects error: {e}") from e

    def fetch_object_metadata(self, bucket_name: str, object_key: str) -> dict:
        """Fetch metadata of an S3 object."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")

            response = self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            # logger.info(f"✅ Fetched metadata for s3://{bucket_name}/{object_key}")
            return response

        except ClientError as e:
            raise RuntimeError(f"S3 fetch metadata error: {e}") from e

    def list_objects(self, bucket_name: str, prefix: str = "") -> list:
        """List objects in an S3 bucket with the given prefix. If prefix is empty, list all objects in the bucket."""

        try:
            bucket_name = bucket_name or self.bucket_name
            if not bucket_name:
                raise ValueError("Bucket name must be provided")

            paginator = self.s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

            objects = []
            for page in page_iterator:
                contents = page.get("Contents", [])
                for obj in contents:
                    objects.append(obj["Key"])

            # logger.info(f"✅ Listed objects in s3://{bucket_name}/{prefix}")
            return objects

        except ClientError as e:
            raise RuntimeError(f"S3 list objects error: {e}") from e


s3_service = S3Service()
