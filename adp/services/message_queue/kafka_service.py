import json
import os
from urllib.parse import urlparse
import boto3
from kafka import KafkaConsumer
from datetime import datetime, timezone
from kafka import KafkaProducer
from ..storage.s3 import S3Service

BOOTSTRAP = "127.0.0.1:19092"   # theo docker compose bạn đang dùng
TOPIC = "ingest-jobs"
GROUP = "ingest-consumer2"


def parse_s3_uri(uri: str) -> tuple[str, str]:
    """
    s3://bucket/key...
    """
    p = urlparse(uri)
    if p.scheme != "s3" or not p.netloc or not p.path:
        raise ValueError(f"Invalid s3 uri: {uri}")
    bucket = p.netloc
    key = p.path.lstrip("/")
    return bucket, key


def send_test_message(msg: dict):
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    producer.send(TOPIC, msg)
    producer.flush()
    print("sent:", msg)


def download_messages():
    s3 = S3Service()
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=GROUP,
        enable_auto_commit=False,              # tự commit sau khi download ok
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    for msg in consumer:
        payload = msg.value
        uri = payload["uri_s3"]
        metadata_id = payload.get("metadata_id")

        try:
            bucket, key = parse_s3_uri(uri)

            # download
            local_path = s3.download_file(key, bucket)
            if not local_path:
                raise Exception("Download failed")

            # nếu tới đây là OK -> commit offset
            consumer.commit()

        except Exception as e:
            # không commit để lần sau đọc lại (hoặc bạn đẩy sang DLQ tuỳ hệ thống)
            print(f"ERROR processing {payload}: {e}")

if __name__ == "__main__":
    send_test_message({
        "uri_s3": "s3://pbl-bulk/paper.pdf",
        "metadata_id": 123,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    download_messages()