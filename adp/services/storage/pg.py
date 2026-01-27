from typing import Any, Dict
from rpds import List
from sqlalchemy.orm import Session
from adp.services.storage.models.document import DocumentModel
from uuid import UUID, uuid4

class PGService:
    # def __init__(self, db: Session):
    #     self.db = db

    def create_document(self, db: Session, data: Dict[str, Any]) -> DocumentModel:
        document = DocumentModel(**data)
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    @staticmethod
    async def get_all(db: Session):
        return db.query(DocumentModel).all()

    @staticmethod
    async def get_by_id(db: Session, document_id: UUID):
        return db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    
    @staticmethod
    async def get_document_by_hash(db: Session, file_hash: str):
        return db.query(DocumentModel).filter(DocumentModel.file_hash == file_hash).first()
    
    @staticmethod
    async def get_documents_by_file_name(db: Session, file_name: str) -> List:
        return db.query(DocumentModel).filter(DocumentModel.file_name.ilike(f"%{file_name}%")).all()
    
    @staticmethod
    async def get_document_by_file_name(db: Session, file_name: str) -> DocumentModel:
        return db.query(DocumentModel).filter(DocumentModel.file_name == file_name).first()
    
    @staticmethod
    async def get_documents_by_file_hash_status(db: Session, file_hash: str, status: str) -> List:
        return db.query(DocumentModel).filter(
            DocumentModel.file_hash == file_hash,
            DocumentModel.status == status
        ).first()

    @staticmethod
    async def create(db: Session, document: DocumentModel):
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    @staticmethod
    async def update_status(db: Session, document_id: UUID, status: str):
        document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if document:
            document.status = status
            db.commit()
            db.refresh(document)
        return document
    
    @staticmethod
    async def update_output_uri(db: Session, document_id: UUID, s3_output_uri: str):
        """Update s3_output_uri for a document"""
        document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if document:
            document.s3_output_uri = s3_output_uri
            db.commit()
            db.refresh(document)
        return document
    
    @staticmethod
    async def update_file_hash(db: Session, document_id: UUID, file_hash: str):
        document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if document:
            document.file_hash = file_hash
            db.commit()
            db.refresh(document)
        return document

    @staticmethod
    async def delete(db: Session, document_id: UUID):
        document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if document:
            db.delete(document)
            db.commit()
        return document
    
    @staticmethod
    async def delete_all(db: Session):
        deleted = db.query(DocumentModel).delete()
        db.commit()
        return deleted


