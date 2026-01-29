from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from adp.services.storage.redis_cache import redis_client

router = APIRouter(prefix="/api/v1/cache", tags=["Cache"])

@router.get("/keys", response_model=List[str])
async def list_cache_keys(pattern: str = Query("*", description="Tìm kiếm key theo pattern (ví dụ: 'user:*')")):
    """
    Show all keys in the cache matching the given pattern.
    """
    try:
        keys = await redis_client._redis.keys(pattern)
        return keys
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching keys: {str(e)}")

@router.get("/value/{key}")
async def get_cache_value(key: str):
    """
    Show the value of a specific key in the cache.
    """
    value = await redis_client.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": value}

@router.delete("/clean/{key}")
async def delete_cache_key(key: str):
    """
    Remove a specific key from the cache.
    """
    result = await redis_client._redis.delete(key)
    if result == 0:
        raise HTTPException(status_code=404, detail="Key not found or already deleted")
    return {"message": f"Deleted key: {key}"}

@router.post("/flush")
async def flush_all_cache():
    """
    Remove all keys from all databases.
    """
    try:
        if redis_client._redis is None:
            await redis_client.connect()
            
        await redis_client._redis.flushall(asynchronous=True) 
        
        return {"status": "success", "message": "Redis cache flushed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flush failed: {str(e)}")