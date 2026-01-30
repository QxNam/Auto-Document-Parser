import asyncio
import os
from time import time
from prometheus_client import start_http_server  # Để expose metrics endpoint trên HTTP server
from adp.services.monitoring.metrics import metrics  # Import metrics helper để track worker metrics

from anyio import Path

from adp.services.data_source.S3 import S3DataSource
from adp.services.message_queue.kafka_message_queue import kafka_service
from adp.services.observer.observer_manager import ObserverManager
from adp.services.storage.models.message import MetadataMessage, ProcessingStatus
from adp.services.storage.pg import PGService
from adp.services.storage.redis_cache import redis_client
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
        self.observer_manager = ObserverManager()

    async def process_task(self, msg_body: dict):
        """Logic to process actual file parsing"""
        # METRICS: Bắt đầu đo thời gian processing
        start_time = time()
        
        # recieved message
        message = MetadataMessage(**msg_body)

        # pull file
        file_obj = self.s3_pull_service.pull(s3_uri=message.s3_uri)
        logger.info(f"🚀 Received file: {message.file_name} (ID: {message.metadata_id})")

        db = SessionLocal()
        await PGService.update_status(db, message.metadata_id, status=ProcessingStatus.PROCESSING)
        
        # Extract file type từ filename để track metrics
        # Ví dụ: "document.pdf" -> "pdf"
        file_type = message.file_name.split('.')[-1].lower() if '.' in message.file_name else 'unknown'
        
        try:
            validate_file_result = validate_file(file_obj=file_obj, file_name=message.file_name)
            if not validate_file_result:
                logger.warning(f"File validation failed for file: {message.file_name} (ID: {message.metadata_id})")
                await PGService.update_status(db, message.metadata_id, status=ProcessingStatus.FAILED)
                return

            result = self.parse.parse(file_obj=file_obj, file_name=message.file_name)
            
            # Observer
            doc = await PGService.get_by_id(db, message.metadata_id)
            results = await self.observer_manager.send(data=result, file_name=message.file_name, task_id=message.metadata_id, file_hash=doc.file_hash)
            await PGService.update_output_uri(
                db=db,
                document_id=message.metadata_id,
                s3_output_uri=results.get("s3")
            )
            
            await PGService.update_status(db, message.metadata_id, status=ProcessingStatus.COMPLETED)
            
            # METRICS: Track successful task completion
            metrics.track_task_completion(status='completed')
            
            # METRICS: Track processing duration
            # duration_seconds = thời gian từ lúc bắt đầu process_task đến giờ
            duration_seconds = time() - start_time
            metrics.track_processing_duration(
                file_type=file_type,
                parser_engine='auto',  # TODO: Lấy từ settings.ENGINE nếu cần chi tiết hơn
                duration_seconds=duration_seconds
            )
            
            logger.info(f"✅ Finished at {time()}")

        except Exception as e:
            logger.error(f"❌ Parse error for {message.metadata_id}: {e}")
            await PGService.update_status(db, message.metadata_id, status=ProcessingStatus.FAILED)
            
            # METRICS: Track failed task
            metrics.track_task_completion(status='failed')
        finally:
            db.close()

    async def start(self):
        """Start the worker to consume messages and process tasks."""
        logger.info("=== Parse Worker Starting ===")
        
        # =============================================================================
        # Start Prometheus Metrics Server
        # =============================================================================
        # Expose metrics endpoint tại port 9000
        # Port này đã được define trong docker-compose.yml (line 122)
        # Prometheus sẽ scrape http://adp_worker_parse:9000/metrics
        try:
            start_http_server(9000)
            logger.info("📊 Metrics server started on port 9000")
            logger.info("📊 Metrics endpoint: http://localhost:9000/metrics")
            
            # METRICS: Set worker active
            metrics.set_active_workers(1)
        except Exception as e:
            logger.warning(f"⚠️ Failed to start metrics server: {e}")
            logger.warning("⚠️ Worker will continue without metrics endpoint")

        await redis_client.connect()

        try:
            await self.kafka_service.start_consuming_async(
                topic=self.topic,
                group_id=self.group_id,
                callback=self.process_task,
            )
        finally:
            await redis_client.close()

if __name__ == "__main__":
    worker = ParseWorker()
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
