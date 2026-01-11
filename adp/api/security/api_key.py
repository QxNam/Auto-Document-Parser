from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from adp.configs.settings import settings

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == settings.SECRET_API_KEY: # Giả định key lưu trong .env
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
