import json
import os
from urllib.parse import urlparse
import boto3
from kafka import KafkaConsumer
from datetime import datetime, timezone
from kafka import KafkaProducer
from adp.configs import settings
from ..storage.s3 import S3Service
from adp.configs.logger import get_logger

logger = get_logger(__name__)



def parse_s3_uri(uri: str) -> tuple[str, str]:
    p = urlparse(uri)
    if p.scheme != "s3" or not p.netloc or not p.path:
        logger.error(f"Invalid s3 uri: {uri}")
    bucket = p.netloc
    key = p.path.lstrip("/")
    return bucket, key


def send_test_message(msg: dict):
    producer = KafkaProducer(
        bootstrap_servers=settings.BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    producer.send(settings.TOPIC, msg)
    producer.flush()
    logger.info(f"sent: {msg}")


def download_messages():
    s3 = S3Service()
    consumer = KafkaConsumer(
        settings.TOPIC,
        bootstrap_servers=settings.BOOTSTRAP,
        group_id=settings.GROUP,
        enable_auto_commit=False,        
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    for msg in consumer:
        payload = msg.value
        uri = payload["uri_s3"]
        metadata_id = payload.get("metadata_id")

        try:
            bucket, key = parse_s3_uri(uri)
            local_path = s3.download_file(key, bucket)
            if not local_path:
                logger.error("Download failed")

            consumer.commit()

        except Exception as e:
            logger.error(f"ERROR processing {payload}: {e}")