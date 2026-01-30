import asyncio
import hashlib
import io
import json
import time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from adp.api.exception import exc
from adp.configs.logger import api_logger as logger
from adp.configs.settings import settings
from adp.services.message_queue.kafka_message_queue import kafka_service
from adp.services.storage.models.message import MetadataMessage, ProcessingStatus
from adp.services.storage.pg import PGService
from adp.services.storage.redis_cache import redis_client
from adp.services.storage.s3 import s3_service
from adp.utils.helpers import get_file_hash
from adp.utils.wait_worker import wait_for_worker_signal

KAFKA_TOPIC_NAME = settings.KAFKA_TOPIC_NAME


class FileService:
    def __init__(self):
        self.file_hash = None
        self.pg_instance = PGService()

    async def send_to_queue(self, db: Session, file: bytes, file_name: str, metadata_str: str):
        """
        Saves the file and sends a message to the processing queue.
        1. Checks file size and type.
        2. Saves the file to S3.
        3. Get S3 URI save metadata to DB.
        4. Publishes a message to Kafka topic for processing.
        """
        try:
            file_obj = io.BytesIO(file)
            file_size = len(file)
            content_type = file_name.split(".")[-1]

            # Step 1: Validate file
            self._check_file_size(file)
            self._check_file_type(file_name)
            logger.info(f"[Step-01] File {file_name} passed validation checks.")

            # check duplicate
            file_exist = await self._check_file_exist(file_name=file_name, file=file, db=db)
            if file_exist:
                raise exc.FileDuplicateError(f"'{file_name}' is already existed!")

            # Step 2: Upload file to S3
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
            s3_response = s3_service.upload_fileobj(
                file_obj=file_obj, bucket_name=settings.S3_BUCKET_NAME, object_key=f"upload/{timestamp}_{file_name}"
            )

            if s3_response.get("status") is not True:
                raise exc.S3UploadError("[Step-02] Failed to upload file to S3.")

            logger.info(f"[Step-02] File {file_name} uploaded to S3 at {s3_response.get('uri')}.")
            s3_uri = s3_response.get("uri")

            # Step 3: Save metadata to DB
            metadata = json.loads(metadata_str) if metadata_str else {}
            doc_data = {
                "s3_uri": s3_uri,
                "file_name": file_name,
                "file_size": file_size,
                "file_hash": self.file_hash,
                "content_type": content_type,
                "status": "pending",
                "metadata_info": metadata,
            }
            doc = self.pg_instance.create_document(db, data=doc_data)
            logger.info(f"[Step-03] Document metadata saved to DB with ID {doc.id}.")

            # Step 4: Publish message to Kafka
            time_current = int(time.time())
            metadata_msg = MetadataMessage(
                metadata_id=str(doc.id),
                s3_uri=s3_uri,
                status=ProcessingStatus.PENDING,
                time=time_current,
                file_size=file_size,
                file_name=file_name,
            )
            message = metadata_msg.to_dict()

            status_push = await kafka_service.publish_message_async(topic=KAFKA_TOPIC_NAME, message=message)
            if not status_push:
                raise exc.MessageQueueError("[Step-04] Failed to publish message to Kafka.")
            logger.info(f"[Step-04] Message published to Kafka topic {KAFKA_TOPIC_NAME} for document ID {doc.id}.")

            return message

        except Exception as e:
            logger.error(f"Error in send_to_queue: {e}", exc_info=True)
            raise e

    async def parse(self, db: Session, file: bytes, file_name: str, metadata_str: str):
        # Tính hash ngay tại cửa ngõ
        file_hash = hashlib.sha256(file).hexdigest()
        self.file_hash = file_hash  # Lưu vào instance để dùng cho Step 3 bên dưới

        # --- BƯỚC 1: KIỂM TRA REDIS (FASTEST) ---
        cache_key = f"cache:file:{file_hash}"
        cached_result = await redis_client.get(cache_key)
        if cached_result:
            logger.info(f"Redis Cache hit: {file_name}")
            return json.loads(cached_result)

        # --- BƯỚC 2: KIỂM TRA DB (DATABASE FALLBACK) ---
        existing_doc = await self.pg_instance.get_documents_by_file_hash_status(
            db, file_hash=file_hash, status=ProcessingStatus.COMPLETED
        )
        if existing_doc:
            logger.info(f"DB Cache hit: {file_name}")
            result = {
                "metadata_id": str(existing_doc.id),
                "s3_uri": existing_doc.s3_output_uri,  # Trả về file đã xử lý
                "status": existing_doc.status,
                "file_name": existing_doc.file_name,
            }
            # Tiện tay cập nhật ngược lại Redis để lần sau nhanh hơn
            await redis_client.set(cache_key, result, ex=86400)
            return result

        # --- BƯỚC 3: GỬI VÀO QUEUE & CHỜ SIGNAL ---
        result_msg = await self.send_to_queue(db, file, file_name, metadata_str)
        task_id = result_msg["metadata_id"]

        try:
            # Wait for worker signal with timeout
            final_result = await wait_for_worker_signal(task_id, timeout=300)
            return final_result

        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=408, detail="Worker is taking too long. Processing will continue in background."
            ) from None

    def _check_file_size(self, file_content: bytes):
        """
        Checks if the file size is within the allowed limit.
        """
        max_size_mb = settings.MAX_FILE_SIZE_MB or 10
        file_size_mb = len(file_content) / (1024 * 1024)
        logger.debug(f"> File size: {file_size_mb:.2f} / {max_size_mb} MB.")

        if file_size_mb == 0:
            raise exc.FileValidationError("File is empty.")

        if file_size_mb > max_size_mb:
            raise exc.FileValidationError(
                f"File size {file_size_mb:.2f} MB exceeds the maximum allowed size of {max_size_mb} MB."
            )

    def _check_file_type(self, file_name: str):
        """
        Checks if the file type is allowed based on its extension.
        """
        allowed_extensions = (
            settings.ALLOWED_FILE_EXTENSIONS.split(",")
            if settings.ALLOWED_FILE_EXTENSIONS
            else [".pdf", ".docx", ".txt"]
        )

        file_extension = "." + file_name.split(".")[-1].lower()
        logger.debug(f"> File extension: {file_extension}")

        if not any(file_name.lower().endswith(ext) for ext in allowed_extensions):
            raise exc.FileValidationError(
                f"File type of {file_name} is not allowed. Allowed types: {allowed_extensions}"
            )

    async def _check_file_exist(self, file_name: str, file: bytes, db: Session) -> bool:
        """
        Checks if a file with the same hash already exists in the database.
        """
        documents = await self.pg_instance.get_documents_by_file_name(db, file_name=file_name)
        if not documents:
            self.file_hash = get_file_hash(file)
            return False

        for doc in documents:
            if doc.file_size == len(file):
                return True

            self.file_hash = get_file_hash(file)
            if doc.file_hash == self.file_hash:
                return True

        return False
