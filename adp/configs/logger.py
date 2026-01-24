import sys
from loguru import logger

FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}"

logger.remove()

logger.add(sys.stdout, format=FILE_FORMAT, level="DEBUG")

logger.add(
    "./logs/api.log",
    filter=lambda record: record["extra"].get("layer") == "API",
    level="INFO",
    rotation="50 MB",
    retention="30 days",
    enqueue=True
)

logger.add(
    "./logs/worker.log",
    filter=lambda record: record["extra"].get("layer") == "WORKER",
    level="INFO",
    rotation="50 MB",
    retention="30 days",
    enqueue=True
)

logger.add(
    "./logs/errors.log",
    level="ERROR",
    rotation="100 MB",
    retention="60 days",
    enqueue=True
)


api_logger = logger.bind(layer="API")
worker_logger = logger.bind(layer="WORKER")
default_logger = logger.bind(layer="SYSTEM")
