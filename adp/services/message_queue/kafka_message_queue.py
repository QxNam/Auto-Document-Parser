import asyncio
import json
from typing import Any, Callable, Dict, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from kafka import KafkaConsumer, KafkaProducer

from adp.configs.logger import worker_logger as logger
from adp.configs.settings import settings
from adp.services.message_queue.base_message_queue import BaseMessageQueueService

KAFKA_BOOTSTRAP_SERVERS = settings.KAFKA_BOOTSTRAP_SERVERS
KAFKA_TOPIC_NAME = settings.KAFKA_TOPIC_NAME
KAFKA_CONSUMER_GROUP_ID = settings.KAFKA_CONSUMER_GROUP_ID


class KafkaService(BaseMessageQueueService):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KafkaService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, bootstrap_servers: str = "kafka:9092"):
        if self._initialized:
            return

        self.bootstrap_servers = bootstrap_servers
        self._sync_producer: Optional[KafkaProducer] = None
        self._async_producer: Optional[AIOKafkaProducer] = None
        self._initialized = True
        logger.info(f"KafkaService initialized with servers: {self.bootstrap_servers}")

    @classmethod
    def get_instance(cls):
        """Get instance of KafkaService Singleton."""
        if cls._instance is None:
            cls()
        return cls._instance

    @classmethod
    def close(cls):
        """Close Kafka connections."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("--- Closed Kafka Producer ---")

    # --- Producer Helpers (Lazy Loading) ---

    def _get_sync_producer(self) -> KafkaProducer:
        """Get or create synchronous Kafka producer."""
        if self._sync_producer is None:
            logger.debug("Creating Sync Kafka Producer...")
            self._sync_producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=5,
                acks="all",
                max_in_flight_requests_per_connection=1,
                request_timeout_ms=10000,
            )
        return self._sync_producer

    async def _get_async_producer(self) -> AIOKafkaProducer:
        """Get or create asynchronous Kafka producer."""
        if self._async_producer is None:
            logger.debug("Creating Async Kafka Producer...")
            self._async_producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=10000,
                retry_backoff_ms=100,
            )
            await self._async_producer.start()
        return self._async_producer

    # --- Implement Abstract Methods ---

    def publish_message_sync(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message synchronously to Kafka topic."""
        try:
            topic = topic or KAFKA_TOPIC_NAME
            producer = self._get_sync_producer()
            future = producer.send(topic, value=message)
            record_metadata = future.get(timeout=10)

            logger.info(
                f"✅ Sync Publish Success: topic={record_metadata.topic}, partition={record_metadata.partition}"
            )
            return True
        except Exception as e:
            logger.error(f"❌ Sync Publish Failed to topic {topic}: {str(e)}", exc_info=True)
            return False

    async def publish_message_async(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message asynchronously to Kafka topic."""
        try:
            producer = await self._get_async_producer()
            await producer.send_and_wait(topic, value=message)
            logger.info(f"✅ Async Publish Success to topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"❌ Async Publish Failed to topic {topic}: {str(e)}", exc_info=True)
            return False

    def start_consuming_sync(self, topic: str, group_id: str, callback: Callable[[Dict[str, Any]], Any]) -> None:
        """Start synchronous Kafka consumer for a topic."""
        logger.info(f"--- Starting Sync Consumer for topic: {topic} ---")
        group_id = group_id or KAFKA_CONSUMER_GROUP_ID
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        try:
            for msg in consumer:
                logger.debug(f"Received sync message from {topic}")
                callback(msg.value)
        except Exception as e:
            logger.error(f"❌ Sync Consumer Error on topic {topic}: {e}")
        finally:
            consumer.close()
            logger.info(f"--- Sync Consumer closed for topic: {topic} ---")

    async def start_consuming_async(self, topic: str, group_id: str, callback: Callable[[Dict[str, Any]], Any]) -> None:
        """Start asynchronous Kafka consumer for a topic."""
        logger.info(f"--- Starting Async Consumer for topic: {topic} ---")
        group_id = group_id or KAFKA_CONSUMER_GROUP_ID
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await consumer.start()
        try:
            async for msg in consumer:
                logger.debug(f"Received async message from {topic}")
                if asyncio.iscoroutinefunction(callback):
                    await callback(msg.value)
                else:
                    callback(msg.value)
        except Exception as e:
            logger.error(f"❌ Async Consumer Error on topic {topic}: {e}")
        finally:
            await consumer.stop()
            logger.info(f"--- Async Consumer stopped for topic: {topic} ---")

    async def wait_connection_closed(self):
        """Wait for Kafka connections to close."""
        if self._sync_producer:
            self._sync_producer.close()
        if self._async_producer:
            await self._async_producer.stop()
        logger.info("Kafka Service connections fully closed.")


kafka_service = KafkaService(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
