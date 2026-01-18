import io
import time
import json
from sqlalchemy.orm import Session

from adp.services.storage.s3 import s3_service
from adp.services.storage.pg import PGService
from adp.services.message_queue.kafka_message_queue import kafka_service
from adp.configs.settings import settings
from adp.configs.logger import get_logger
logger = get_logger(layer="API", name=__name__)

KAFKA_TOPIC_NAME = settings.KAFKA_TOPIC_NAME

class FileService:
    async def send_to_queue(self, db: Session, file: bytes, filename: str, metadata_str: str):
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
            content_type = filename.split(".")[-1]

            # Step 1: Validate file
            self._check_file_size(file)
            self._check_file_type(filename)
            logger.info(f"[Step-01] File {filename} passed validation checks.")

            # Step 2: Upload file to S3
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
            s3_response = s3_service.upload_fileobj(
                file_obj=file_obj,
                bucket_name=settings.S3_BUCKET_NAME,
                object_key=f"upload/{timestamp}_{filename}"
            )

            if s3_response.get("status") is not True:
                raise RuntimeError("[Step-02] Failed to upload file to S3.")
            
            logger.info(f"[Step-02] File {filename} uploaded to S3 at {s3_response.get('uri')}.")
            s3_uri = s3_response.get("uri")

            # Step 3: Save metadata to DB
            metadata = json.loads(metadata_str) if metadata_str else {}
            pg_service = PGService()
            doc_data = {
                "s3_uri": s3_uri,
                "file_name": filename,
                "file_size": file_size,
                "content_type": content_type,
                "status": "pending",
                "metadata_info": metadata
            }
            doc = pg_service.create_document(
                db,
                data=doc_data
            )
            logger.info(f"[Step-03] Document metadata saved to DB with ID {doc.id}.")

            # Step 4: Publish message to Kafka
            time_current = int(time.time())
            message = {
                "metadata_id": str(doc.id),
                "s3_uri": s3_uri,
                "status": "pending",
                "time": time_current,
                "file_size": file_size, 
                "filename": filename
            }
            status_push = await kafka_service.publish_message_async(topic=KAFKA_TOPIC_NAME, message=message)
            if not status_push:
                raise RuntimeError("[Step-04] Failed to publish message to Kafka.")
            logger.info(f"[Step-04] Message published to Kafka topic {KAFKA_TOPIC_NAME} for document ID {doc.id}.")

            return message
        
        except Exception as e:
            logger.error(f"Error in send_to_queue: {e}", exc_info=True)
            raise e

    async def parse(self, file_content: bytes):
        pass

    async def test_producer(self, message:json={}):
        time_current = int(time.time())
        message.update({"time": time_current})
        status_push = await kafka_service.publish_message_async(topic=KAFKA_TOPIC_NAME, message=message)
        if not status_push:
            raise RuntimeError("[Producer test] Failed to publish message to Kafka.")
        logger.info(f"[Producer test] Message published to Kafka topic {KAFKA_TOPIC_NAME} at time {time_current}.")

    def _check_file_size(self, file_content: bytes):
        """
        Checks if the file size is within the allowed limit.
        """
        max_size_mb = settings.MAX_FILE_SIZE_MB or 10
        file_size_mb = len(file_content) / (1024 * 1024)
        logger.debug(f"> File size: {file_size_mb:.2f} / {max_size_mb} MB.")

        if file_size_mb == 0:
            raise ValueError("File is empty.")
        
        if file_size_mb > max_size_mb:
            raise ValueError(f"File size {file_size_mb:.2f} MB exceeds the maximum allowed size of {max_size_mb} MB.")
        
    def _check_file_type(self, filename: str):
        """
        Checks if the file type is allowed based on its extension.
        """
        allowed_extensions = settings.ALLOWED_FILE_EXTENSIONS.split(",") if settings.ALLOWED_FILE_EXTENSIONS else [".pdf", ".docx", ".txt"]

        file_extension = "." + filename.split(".")[-1].lower()
        logger.debug(f"> File extension: {file_extension}")

        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"File type of {filename} is not allowed. Allowed types: {allowed_extensions}")
    
