import asyncio
import json

from adp.services.storage.redis_cache import redis_client


async def wait_for_worker_signal(task_id: str, timeout: int) -> dict:
    """
    Listen for completion signal from Worker via Redis Pub/Sub.
    """
    pubsub = redis_client.pubsub()
    channel_name = f"channel:task:{task_id}"
    await pubsub.subscribe(channel_name)

    try:
        return await asyncio.wait_for(_listen_loop(pubsub), timeout=timeout)
    finally:
        await pubsub.unsubscribe(channel_name)


async def _listen_loop(pubsub):
    while True:
        message = await pubsub.get_message()
        if message and message["type"] == "message":
            return json.loads(message["data"])
        await asyncio.sleep(0.2)
