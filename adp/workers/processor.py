import asyncio
import os
import io
from datetime import datetime
from time import time

from adp.services.data_source.S3 import S3DataSource
from adp.services.message_queue.kafka_message_queue import kafka_service
from adp.services.storage.models.message import MetadataMessage, ProcessingStatus
from adp.services.storage.pg import PGService
from adp.services.storage.s3 import s3_service
from adp.services.parse.parse import Parse
from adp.utils.validator import check as validate_file
from adp.configs.settings import settings
from adp.configs.database import SessionLocal
from adp.configs.logger import worker_logger as logger

KAFKA_TOPIC_NAME = settings.KAFKA_TOPIC_NAME
KAFKA_CONSUMER_GROUP_ID = settings.KAFKA_CONSUMER_GROUP_ID
os.makedirs("/tmp/saved", exist_ok=True)
class ParseWorker:
    def __init__(self):
        self.kafka_service = kafka_service
        self.topic = KAFKA_TOPIC_NAME
        self.group_id = KAFKA_CONSUMER_GROUP_ID
        self.parse = Parse()
        self.s3_pull_service = S3DataSource()

    async def process_task(self, msg_body: dict):
        """Logic to process actual file parsing"""
        # recieved message
        message = MetadataMessage(**msg_body)

        # pull file
        file_obj = self.s3_pull_service.pull(s3_uri=message.s3_uri)
        logger.info(f"🚀 Received file: {message.file_name} (ID: {message.metadata_id})")

        db = SessionLocal()
        await PGService.update_status(db, message.metadata_id, status=ProcessingStatus.PROCESSING)
        
        try:
            
            validate_file_result = validate_file(file_obj=file_obj, file_name=message.file_name)
            if not validate_file_result:
                logger.warning(f"File validation failed for file: {message.file_name} (ID: {message.metadata_id})")
                await PGService.update_status(db, message.metadata_id, status=ProcessingStatus.FAILED)
                return

            result = self.parse.parse(file_obj=file_obj, file_name=message.file_name)
            logger.info(f"Parsed content: {result[:100]}")
            
            # create s3 object key
            date_prefix = datetime.now().strftime("%Y/%m/%d")
            object_key = f"outputs/{date_prefix}/{message.metadata_id}.md"
            
            # Convert markdown string to BytesIO
            md_file_obj = io.BytesIO(result.encode('utf-8'))
            
            # Upload markdown to S3
            upload_result = s3_service.upload_fileobj(
                file_obj=md_file_obj,
                bucket_name=settings.S3_BUCKET_NAME,  # hoặc None nếu đã có default
                object_key=object_key,
                extra_args={'ContentType': 'text/markdown'}
            )
            
            s3_output_uri = upload_result['uri']
            logger.info(f"✅ Uploaded markdown to S3: {s3_output_uri}")
            
            # Update database with output URI
            await PGService.update_output_uri(
                db=db,
                document_id=message.metadata_id,
                s3_output_uri=s3_output_uri
            )
            
            logger.info(f"💾 Updated database with output URI: {s3_output_uri}")
            
            await PGService.update_status(db, message.metadata_id, status=ProcessingStatus.COMPLETED)
            logger.info(f"✅ Finished at {time()}")

        except Exception as e:
            logger.error(f"❌ Parse error for {message.metadata_id}: {e}")
            await PGService.update_status(db, message.metadata_id, status=ProcessingStatus.FAILED)
        finally:
            db.close()

    async def start(self):
        """Start the worker to consume messages and process tasks."""
        logger.info("=== Parse Worker Starting ===")
        await self.kafka_service.start_consuming_async(
            topic=self.topic,
            group_id=self.group_id,
            callback=self.process_task,
        )

if __name__ == "__main__":
    worker = ParseWorker()
    asyncio.run(worker.start())
