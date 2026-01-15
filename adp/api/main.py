from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from adp.api.v1.router import router as v1_router

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

app.include_router(v1_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Auto Document Parser API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
