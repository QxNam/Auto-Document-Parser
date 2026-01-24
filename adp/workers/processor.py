import asyncio
import os
from time import time

from adp.services.data_source.S3 import S3DataSource
from adp.services.message_queue.kafka_message_queue import kafka_service
from adp.services.storage.models.message import MetadataMessage, ProcessingStatus
from adp.services.storage.pg import PGService
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
            
            # save parsed result
            output_md_path = f"/tmp/saved/{message.file_name}.md"
            with open(output_md_path, "w", encoding="utf-8") as f:
                f.write(result)
            logger.info(f"Saved parsed markdown to {output_md_path}")

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
