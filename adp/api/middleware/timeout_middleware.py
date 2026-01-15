import asyncio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from adp.configs.logger import get_logger

logger = get_logger(__name__)

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout_seconds: int = 30, exclude_paths: list = None):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request: Request, call_next):
        # Kiểm tra nếu đường dẫn hiện tại nằm trong danh sách loại trừ (như upload)
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        try:
            return await asyncio.wait_for(
                call_next(request), 
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Timeout: {request.method} {request.url.path} vượt quá {self.timeout_seconds}s")
            return JSONResponse(
                status_code=504,
                content={"detail": "Request Timeout", "interval": self.timeout_seconds}
            )
