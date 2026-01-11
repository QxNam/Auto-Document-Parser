from fastapi import FastAPI
from adp.api.routers import documents
from adp.api.middleware.rate_limit import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from adp.configs.database import create_tables

app = FastAPI(
    title="API Auto Document Parser",
    description="API for Auto Document Parser project",
    version="0.0.1",
)

@app.on_event("startup")
async def on_startup():
    try:
        create_tables()
    except Exception:
        pass

# Rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Home"])
async def root():
    return {"message": "Welcome to the Auto Document Parsing API!"}

@app.get("/health", tags=["Home"])
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(documents.router)

