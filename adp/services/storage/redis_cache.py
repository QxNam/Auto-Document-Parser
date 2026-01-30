import json

import redis.asyncio as redis

from adp.configs.logger import api_logger, worker_logger
from adp.configs.settings import settings

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
                    REDIS_URL, encoding="utf-8", decode_responses=True, socket_timeout=5, retry_on_timeout=True
                )
                worker_logger.info("✅ Successfully connected to Redis.")
                api_logger.info("✅ Successfully connected to Redis.")

            except Exception as e:
                raise e

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

    async def flush_all(self):
        """Remove all keys from all databases."""
        if self._redis:
            return await self._redis.flushall()
        return False

    async def get_all_keys(self, pattern: str = "*"):
        """Get all keys (Use SCAN to avoid blocking Redis)"""
        keys = []
        cursor = 0
        while True:
            cursor, partial_keys = await self._redis.scan(cursor=cursor, match=pattern, count=100)
            keys.extend(partial_keys)
            if cursor == 0:
                break
        return keys

    async def close(self):
        if self._redis:
            await self._redis.close()


redis_client = RedisClient()
