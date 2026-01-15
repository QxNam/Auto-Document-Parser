import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from adp.configs.settings import settings

# Cấu hình logging để dễ theo dõi lỗi kết nối
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KafkaSingleton")

KAFKA_BOOTSTRAP_SERVERS = settings.KAFKA_BOOTSTRAP_SERVERS

class KafkaSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("--- Khởi tạo Kafka Producer Singleton ---")
            try:
                cls._instance = KafkaProducer(
                    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                    api_version=(3, 7, 0),
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    acks='all',              # Đảm bảo broker nhận được dữ liệu
                    retries=5,               # Tự động thử lại nếu lỗi mạng
                    max_in_flight_requests_per_connection=1,
                    request_timeout_ms=30000 # Chờ phản hồi tối đa 30s
                )
                logger.info("✅ Kết nối Kafka thành công")
            except KafkaError as e:
                logger.error(f"❌ Không thể kết nối Kafka: {e}")
                raise e
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance

    @classmethod
    def close(cls):
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("--- Đã đóng Kafka Producer ---")

# Tạo một biến global để dễ dàng import
producer = KafkaSingleton.get_instance()
