import json
import redis.asyncio as redis
from adp.configs.settings import settings
from adp.configs.logger import worker_logger as logger

REDIS_URL = settings.REDIS_URL or "redis://localhost:6379/0"

class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._redis = None
        return cls._instance

    async def connect(self):
        """Initialize connection pool."""
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                logger.info("Successfully connected to Redis.")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

    async def get(self, key: str):
        return await self._redis.get(key)

    async def set(self, key: str, value: any, ex: int = None):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await self._redis.set(key, value, ex=ex)

    async def publish(self, channel: str, message: any):
        """Publish message to a channel."""
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        return await self._redis.publish(channel, message)

    def pubsub(self):
        """Return a pubsub object for the API to listen on."""
        return self._redis.pubsub()

    async def close(self):
        if self._redis:
            await self._redis.close()


redis_client = RedisClient()
