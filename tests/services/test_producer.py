import json
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError


def test_kafka_producer():
    # Cấu hình các tham số
    bootstrap_servers = ["kafka:9092"]
    topic_name = "test-topic"

    print(f"--- Đang khởi tạo Producer kết nối tới {bootstrap_servers} ---")

    try:
        # Khởi tạo Producer
        # value_serializer giúp tự động ép kiểu dữ liệu dict sang JSON bytes
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers, value_serializer=lambda v: json.dumps(v).encode("utf-8"), retries=5
        )

        # Dữ liệu thử nghiệm
        data = {"id": 1, "message": "Hello Kafka KRaft!", "timestamp": time.time()}

        print(f"--- Đang gửi message tới topic: {topic_name} ---")

        # Gửi message
        # Kafka mặc định cho phép tự động tạo topic khi gửi message lần đầu
        # (thuộc tính auto.create.topics.enable mặc định là true)
        future = producer.send(topic_name, value=data)

        # Chờ đợi kết quả gửi (synchronous check)
        record_metadata = future.get(timeout=10)

        print("✅ Gửi message thành công!")
        print(f"Topic: {record_metadata.topic}")
        print(f"Partition: {record_metadata.partition}")
        print(f"Offset: {record_metadata.offset}")

    except KafkaError as e:
        print(f"❌ Lỗi kết nối hoặc gửi message: {e}")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
    finally:
        if "producer" in locals():
            producer.close()
            print("--- Đã đóng Producer ---")


if __name__ == "__main__":
    test_kafka_producer()
