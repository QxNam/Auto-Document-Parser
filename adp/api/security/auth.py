from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from adp.configs.settings import settings

# Header required from client
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def validate_api_key(api_key_header_value: str = Security(api_key_header)):
    """
    Validate `X-API-KEY` from request headers against `settings.SECRET_API_KEY`.
    The secret is loaded from environment via `.env`.
    """
    expected_key = settings.SECRET_API_KEY
    if not expected_key or api_key_header_value != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials: Invalid API Key",
        )
    return api_key_header_value
