"""
Kafka Message Queue với Prometheus Metrics

Service này quản lý Kafka producer/consumer và track metrics về:
- Số messages produced/consumed
- Kafka lag
- Thời gian produce message
- Lỗi Kafka

HƯỚNG DẪN SỬ DỤNG:
Khi bạn implement Kafka producer/consumer, hãy sử dụng các classes dưới đây.
"""

import time
from typing import Optional
from adp.configs.logger import get_logger

# Import metrics
from adp.monitoring import (
    kafka_messages_produced_total,
    kafka_messages_consumed_total,
    kafka_message_lag,
    kafka_produce_duration_seconds,
    kafka_consumer_offset,
    kafka_produce_errors_total,
)

logger = get_logger(__name__)


class KafkaProducerWithMetrics:
    """
    Kafka Producer wrapper với Prometheus metrics tracking.
    
    Sử dụng:
        producer = KafkaProducerWithMetrics()
        producer.produce(topic="document-processing", message={"file_path": "/path/to/file"})
    """
    
    def __init__(self):
        # TODO: Initialize Kafka producer
        # from kafka import KafkaProducer
        # self.producer = KafkaProducer(...)
        pass
    
    def produce(self, topic: str, message: dict) -> bool:
        """
        Produce message vào Kafka topic và track metrics.
        
        Args:
            topic: Kafka topic name
            message: Message data (dict)
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        # Bắt đầu đếm thời gian
        start_time = time.time()
        
        try:
            # TODO: Produce message
            # self.producer.send(topic, value=message)
            # self.producer.flush()
            
            # Tính thời gian produce
            duration = time.time() - start_time
            
            # ✅ TRACK METRICS - THÀNH CÔNG
            kafka_produce_duration_seconds.labels(
                topic=topic
            ).observe(duration)
            
            kafka_messages_produced_total.labels(
                topic=topic
            ).inc()
            
            logger.info(f"Produced message to topic {topic} in {duration:.3f}s")
            return True
            
        except Exception as e:
            # ❌ TRACK METRICS - LỖI
            error_type = e.__class__.__name__
            
            kafka_produce_errors_total.labels(
                topic=topic,
                error_type=error_type
            ).inc()
            
            logger.error(f"Failed to produce message to {topic}: {str(e)}")
            return False


class KafkaConsumerWithMetrics:
    """
    Kafka Consumer wrapper với Prometheus metrics tracking.
    
    Sử dụng:
        consumer = KafkaConsumerWithMetrics(topic="document-processing", group_id="adp-workers")
        for message in consumer.consume():
            # Process message
            pass
    """
    
    def __init__(self, topic: str, group_id: str = "default"):
        self.topic = topic
        self.group_id = group_id
        
        # TODO: Initialize Kafka consumer
        # from kafka import KafkaConsumer
        # self.consumer = KafkaConsumer(
        #     topic,
        #     group_id=group_id,
        #     ...
        # )
    
    def consume(self):
        """
        Consume messages từ Kafka topic và track metrics.
        
        Yields:
            message: Kafka message
        """
        # TODO: Implement consume loop
        # for message in self.consumer:
        #     # Track metrics
        #     self._track_consume_metrics(message)
        #     yield message
        pass
    
    def _track_consume_metrics(self, message):
        """Track metrics khi consume message."""
        partition = message.partition
        offset = message.offset
        
        # ✅ TRACK METRICS - CONSUMED
        kafka_messages_consumed_total.labels(
            topic=self.topic,
            consumer_group=self.group_id
        ).inc()
        
        # Update consumer offset
        kafka_consumer_offset.labels(
            topic=self.topic,
            partition=str(partition),
            consumer_group=self.group_id
        ).set(offset)
        
        # TODO: Calculate lag
        # lag = latest_offset - current_offset
        # kafka_message_lag.labels(
        #     topic=self.topic,
        #     partition=str(partition),
        #     consumer_group=self.group_id
        # ).set(lag)
        
        logger.debug(f"Consumed message from {self.topic} partition {partition} offset {offset}")


# ============================================================================
# VÍ DỤ SỬ DỤNG
# ============================================================================

# # Producer
# producer = KafkaProducerWithMetrics()
# producer.produce(
#     topic="document-processing",
#     message={"file_path": "/data/document.pdf", "user_id": 123}
# )
#
# # Consumer
# consumer = KafkaConsumerWithMetrics(
#     topic="document-processing",
#     group_id="adp-workers"
# )
# for message in consumer.consume():
#     # Process message
#     process_document(message.value["file_path"])
