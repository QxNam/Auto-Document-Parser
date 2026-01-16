from adp.services.message_queue.kafka_message_queue import kafka_service
from adp.configs.settings import settings

from adp.configs.logger import get_logger
logger = get_logger(__name__)

KAFKA_TOPIC_UPLOADS = settings.KAFKA_TOPIC_UPLOADS
KAFKA_CONSUMER_GROUP_ID = settings.KAFKA_CONSUMER_GROUP_ID

import asyncio
from time import time
from adp.services.message_queue.kafka_message_queue import kafka_service
from adp.configs.database import SessionLocal
from adp.configs.logger import get_logger

logger = get_logger(__name__)

class WorkerParser:
    def __init__(self):
        self.kafka_service = kafka_service
        self.topic = KAFKA_TOPIC_UPLOADS
        self.group_id = KAFKA_CONSUMER_GROUP_ID

    async def process_task(self, msg_body: dict):
        """Logic xử lý parse file thực tế"""
        doc_id = msg_body.get("document_id")
        s3_uri = msg_body.get("s3_uri")
        
        db = SessionLocal()
        
        try:
            logger.info(f"🚀 Processing doc: {doc_id} from {s3_uri}")
            
            # 1. Update status thành 'processing'
            # await PGService.update_document(db, doc_id, status="processing")

            # 2. Thực hiện Parse file (Giả lập logic của bạn)
            # result = await self.parser_logic.parse(s3_uri)
            await asyncio.sleep(10) # Giả lập thời gian parse

            # 3. Update kết quả thành 'completed'
            # await PGService.update_document(db, doc_id, status="completed")
            logger.info(f"✅ Finished doc: {doc_id}")

        except Exception as e:
            logger.error(f"❌ Parse error for {doc_id}: {e}")
            # pg_service.update_document(doc_id, status="failed")
        finally:
            db.close()

    async def start(self):
        """Bắt đầu lắng nghe từ Kafka"""
        # Sử dụng hàm start_consuming_async đã thiết kế ở KafkaService
        await self.kafka_service.start_consuming_async(
            topic=self.topic,
            callback=self.process_task
        )

if __name__ == "__main__":
    worker = WorkerParser()
    asyncio.run(worker.start())