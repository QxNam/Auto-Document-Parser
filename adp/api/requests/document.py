from typing import Any, Optional

from pydantic import BaseModel, Field


class DocumentCreateRequest(BaseModel):
    s3_uri: str
    file_name: str
    file_size: int
    content_type: Optional[str] = None
    metadata_info: Optional[dict[str, Any]] = Field(None, alias="metadata")


class DocumentUpdateStatusRequest(BaseModel):
    document_id: str
    status: str = Field(..., pattern="^(pending|processing|completed|failed)$")
