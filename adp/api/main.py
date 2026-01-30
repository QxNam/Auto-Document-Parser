from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from adp.api.middleware.rate_limit import limiter
from adp.api.middleware.timeout_middleware import TimeoutMiddleware
from adp.api.routers import cache_router, document_router, file_router, s3_router
from adp.configs.database import create_tables
from adp.configs.logger import api_logger as logger
from adp.configs.settings import settings
from adp.services.storage.redis_cache import redis_client

ENV = settings.MODE or "dev"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing database tables...")
        create_tables()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    await redis_client.connect()
    yield
    await redis_client.close()


if ENV == "prod":
    app = FastAPI(
        title="API Auto Document Parse",
        description="API for Auto Document Parse project",
        version="0.0.1",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
else:
    app = FastAPI(
        title="API Auto Document Parse",
        description="API for Auto Document Parse project",
        version="0.0.1",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

# Rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    TimeoutMiddleware,
    timeout_seconds=settings.API_TIMEOUT_INTERVAL or 30,
    exclude_paths=["/api/v1/file/upload", "/api/v1/file/view"],
)


@app.middleware("http")
async def restrict_docs_to_localhost(request: Request, call_next):
    path = request.url.path
    restricted_paths = ["/docs", "/redoc", "/openapi.json"]

    if path in restricted_paths:
        host = request.headers.get("host", "")
        if not any(local_host in host for local_host in ["localhost", "127.0.0.1"]):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

    response = await call_next(request)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Home"])
async def root():
    return {"message": "Welcome to the Auto Document Parse API!"}


@app.get("/health", tags=["Home"])
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(file_router.router)
app.include_router(document_router.router)
app.include_router(s3_router.router)
app.include_router(cache_router.router)
