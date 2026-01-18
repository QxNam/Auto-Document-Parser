import os
import sys
from loguru import logger

os.makedirs("./logs", exist_ok=True)

LOGGER_NAME_DEFAULT = "ADP"
FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[layer]} | {name}:{line} | {message}"


logger.add(
    "./logs/all.log",
    level="INFO",
    rotation="50 MB",
    compression="zip",
    format=FILE_FORMAT,
    enqueue=True
)

# File handler cho lỗi
logger.add(
    "./logs/errors.log",
    level="ERROR",
    rotation="50 MB",
    format=FILE_FORMAT,
    enqueue=True
)

def get_logger(layer: str, name: str = "ADP"):
    return logger.bind(layer=layer, name=name)
