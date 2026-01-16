from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from adp.services.storage.pg import PGService
from adp.configs.database import get_db
from adp.services.storage.models.document import DocumentModel
from adp.api.requests.document import DocumentCreateRequest, DocumentUpdateStatusRequest
from adp.api.responses.document import DocumentResponse
from adp.api.security.api_key import validate_api_key
from adp.api.middleware.rate_limit import limiter

router = APIRouter(
    prefix="/documents", 
    tags=["Documents"],
    responses={
        status.HTTP_200_OK: {"description": "OK"},
        status.HTTP_201_CREATED: {"description": "Created"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_408_REQUEST_TIMEOUT: {"description": "Request timeout"},
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {"description": "Request entity too large"},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"description": "Unsupported media type"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    }
)

@router.get("/", response_model=List[DocumentResponse])
@limiter.limit("60/minute")
async def read_documents(
    request: Request, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    return await PGService.get_all(db)

@router.get("/{document_id}", response_model=DocumentResponse)
async def read_document(
    document_id: str, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    db_doc = await PGService.get_by_id(db, document_id)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("60/minute")
async def create_document(
    request: Request,
    payload: DocumentCreateRequest, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    # Ánh xạ từ Request Schema sang SQLAlchemy Model
    new_doc = DocumentModel(**payload.model_dump())
    return await PGService.create(db, new_doc)

@router.put("/status", response_model=DocumentResponse)
async def update_doc_status(
    payload: DocumentUpdateStatusRequest, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    db_doc = await PGService.update_status(db, payload.document_id, payload.status)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    success = await PGService.delete(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
