from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from adp.services.storage.pg import PGService
from adp.configs.database import get_db
from adp.services.storage.models.document import DocumentModel
from adp.api.requests.document import DocumentCreateRequest, DocumentUpdateStatusRequest
from adp.api.responses.document import DocumentResponse
from adp.api.security.auth import validate_api_key
from adp.api.middleware.rate_limit import limiter

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/", response_model=List[DocumentResponse])
@limiter.limit("5/minute")
async def read_documents(
    request: Request, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    return PGService.get_all(db)

@router.get("/{document_id}", response_model=DocumentResponse)
async def read_document(
    document_id: UUID, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    db_doc = PGService.get_by_id(db, document_id)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_document(
    request: Request,
    payload: DocumentCreateRequest, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    # Ánh xạ từ Request Schema sang SQLAlchemy Model
    new_doc = DocumentModel(**payload.model_dump())
    return PGService.create(db, new_doc)

@router.patch("/{document_id}/status", response_model=DocumentResponse)
async def update_doc_status(
    document_id: UUID, 
    payload: DocumentUpdateStatusRequest, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    db_doc = PGService.update_status(db, document_id, payload.status)
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_doc

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID, 
    db: Session = Depends(get_db), 
    _ = Depends(validate_api_key)
):
    success = PGService.delete(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
