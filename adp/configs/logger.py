from loguru import logger

LOGGER_NAME_DEFAULT = "dpe_logger".upper()
FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} |{file}:{line} | {message}"
logger.add(
    "logs/all_logs.log",
    level="DEBUG",
    format=FILE_FORMAT,
    rotation="50 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
    encoding="utf-8",
)

logger.add(
    "logs/errors.log",
    level="ERROR",
    format=FILE_FORMAT,
    rotation="50 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
    encoding="utf-8",
)


def get_logger(name: str = LOGGER_NAME_DEFAULT):
    return logger.bind(name=name)
