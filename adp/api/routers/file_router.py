import asyncio
from fastapi import APIRouter, Request, UploadFile, status, HTTPException, File, Depends
from typing import Dict
from sqlalchemy.orm import Session

from adp.api.responses.upload import UploadResponse, ViewResponse
from adp.api.services.file_service import FileService
from adp.utils.wait_worker import wait_for_worker_signal
from adp.configs.database import get_db
from adp.configs.settings import settings
from adp.api.middleware.rate_limit import limiter

file_service = FileService()
API_TIMEOUT_INTERVAL = settings.API_TIMEOUT_INTERVAL or 30

router = APIRouter(
    prefix="/api/v1/file", 
    tags=["File"],
    responses={
        status.HTTP_200_OK: {"description": "OK"},
        status.HTTP_201_CREATED: {"description": "Created"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_408_REQUEST_TIMEOUT: {"description": "Request timeout"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    }
)

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("30/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(..., description="File to be uploaded and processed"),
    metadata: str = File("", description="Optional metadata in JSON string format"),
    db: Session = Depends(get_db)
) -> UploadResponse:
    """
    Uploads a file to parser processing.
    """
    try:
        result: Dict[str, str] = await file_service.send_to_queue(db, await file.read(), file.filename, metadata)
        return UploadResponse(**result)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during file upload: {str(e)}",
        )
    
@router.post("/view", status_code=status.HTTP_200_OK)
@limiter.limit("30/minute")
async def view_file(
    request: Request,
    file: UploadFile = File(...),
    metadata: str = File(""),
    db: Session = Depends(get_db)
):
    try:
        result: Dict[str, str] = await file_service.parse(db, await file.read(), file.filename, metadata)
        return result #UploadResponse(**result)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during file upload: {str(e)}",
        )
