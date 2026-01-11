from sqlalchemy import Column, String, BigInteger, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from adp.configs.database import Base

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    s3_uri = Column(String, unique=True, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    content_type = Column(String(100))
    status = Column(String(20), default='pending')
    metadata_info = Column(JSONB, name="metadata")
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))
