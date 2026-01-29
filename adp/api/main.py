from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from adp.api.middleware.timeout_middleware import TimeoutMiddleware
from adp.api.routers import document_router, file_router, s3_router, cache_router
from adp.api.middleware.rate_limit import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from adp.configs.settings import settings
from adp.services.storage.redis_cache import redis_client
from adp.configs.database import create_tables
from adp.configs.logger import api_logger as logger

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

app = FastAPI(
    title="API Auto Document Parse",
    description="API for Auto Document Parse project",
    version="0.0.1",
    lifespan=lifespan
)


# Rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    TimeoutMiddleware, 
    timeout_seconds=settings.API_TIMEOUT_INTERVAL or 30,
    exclude_paths=["/api/v1/file/upload", "/api/v1/file/view"]
)
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

