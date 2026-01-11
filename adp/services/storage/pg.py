from sqlalchemy.orm import Session
from adp.services.storage.models.document import DocumentModel
from uuid import UUID

class PGService:
    @staticmethod
    def get_all(db: Session):
        return db.query(DocumentModel).all()

    @staticmethod
    def get_by_id(db: Session, document_id: UUID):
        return db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    
    @staticmethod
    def create(db: Session, document: DocumentModel):
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    @staticmethod
    def update_status(db: Session, document_id: UUID, status: str):
        document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if document:
            document.status = status
            db.commit()
            db.refresh(document)
        return document
    
    @staticmethod
    def delete(db: Session, document_id: UUID):
        document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if document:
            db.delete(document)
            db.commit()
        return document
