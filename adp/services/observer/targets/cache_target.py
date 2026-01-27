from time import time

from pathlib import Path
from adp.configs.settings import settings
from adp.services.observer.base_observer import BaseObserver
from adp.services.storage.redis_cache import redis_client
from adp.configs.logger import worker_logger as logger

class CacheTarget(BaseObserver):
    def __init__(self):
        self.local_dir = Path(settings.LOCAL_SAVED_DIR)
        self.local_dir.mkdir(parents=True, exist_ok=True)

    async def update(self, data: str, file_name: str, *args, **kwargs) -> dict:
        """
        Cache the result data in Redis and publish a signal for waiting API.
        """
        task_id = kwargs.get("task_id")
        file_hash = kwargs.get("file_hash")
        clean_name = Path(file_name).with_suffix('.md')
        output_path = self.local_dir / clean_name

        if not task_id:
            logger.error("[CacheTarget] task_id is missing in update kwargs")
            return {"status": "failed", "error": "task_id missing"}

        try:
            result_payload = {
                "metadata_id": task_id,
                "status": "completed",
                "file_name": file_name,
                "content": data,
                "local_path": str(output_path),
                "time_completed": int(time())
            }

            # 1. Publish Signal (Cho API đang treo)
            channel = f"channel:task:{task_id}"
            await redis_client.publish(channel, result_payload)
            logger.info(f"[CacheTarget] Signal sent to {channel}")

            # 2. Caching theo nội dung file (Dùng cho API check-hit)
            if file_hash:
                cache_key = f"cache:file:{file_hash}"
                await redis_client.set(cache_key, result_payload, ex=86400)
                logger.info(f"[CacheTarget] Data cached for hash: {file_hash}")

            return result_payload

        except Exception as e:
            logger.error(f"[CacheTarget] Redis Error: {e}")
            return {"status": "failed", "error": str(e)}

    async def close(self):
        pass
