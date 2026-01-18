import asyncio
from time import time

from adp.services.message_queue.kafka_message_queue import kafka_service
from adp.configs.settings import settings
from adp.configs.database import SessionLocal

from adp.configs.logger import get_logger
logger = get_logger(layer="WORKER", name=__name__)

KAFKA_TOPIC_NAME = settings.KAFKA_TOPIC_NAME
KAFKA_CONSUMER_GROUP_ID = settings.KAFKA_CONSUMER_GROUP_ID

class ParserWorker:
    def __init__(self):
        self.kafka_service = kafka_service
        self.topic = KAFKA_TOPIC_NAME
        self.group_id = KAFKA_CONSUMER_GROUP_ID

    async def process_task(self, msg_body: dict):
        """Logic to process actual file parsing"""
        doc_id = msg_body.get("document_id")
        s3_uri = msg_body.get("s3_uri")
        
        db = SessionLocal()
        
        try:
            logger.info(f"🚀 Processing at {time()}")
            
            # 1. Update status to 'processing'
            # await PGService.update_document(db, doc_id, status="processing")

            # 2. Thực hiện Parse file (Giả lập logic của bạn)
            # result = await self.parser_logic.parse(s3_uri)
            await asyncio.sleep(10) # Giả lập thời gian parse

            # 3. Update kết quả thành 'completed'
            # await PGService.update_document(db, doc_id, status="completed")
            logger.info(f"✅ Finished at {time()}")

        except Exception as e:
            logger.error(f"❌ Parse error for {doc_id}: {e}")
            # pg_service.update_document(doc_id, status="failed")
        finally:
            db.close()

    async def start(self):
        """Start the worker to consume messages and process tasks."""
        logger.info("=== Parser Worker Starting ===")
        await self.kafka_service.start_consuming_async(
            topic=self.topic,
            group_id=self.group_id,
            callback=self.process_task,
        )

if __name__ == "__main__":
    worker = ParserWorker()
    asyncio.run(worker.start())
