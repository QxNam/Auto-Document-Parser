from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adp.api.routers import s3

app = FastAPI(
    title="API Auto Document Parser",
    description="API for Auto Document Parser project",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(s3.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Auto Document Parser API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
