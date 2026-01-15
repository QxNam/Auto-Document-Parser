from fastapi import APIRouter
from api.v1.routes.file import router as file_router
from api.v1.routes.view import router as view_router

router = APIRouter()
router.include_router(file_router)
router.include_router(view_router)
