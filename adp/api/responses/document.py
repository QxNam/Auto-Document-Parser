from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: UUID
    s3_uri: str
    file_name: str
    file_size: int
    file_hash: Optional[str]
    content_type: Optional[str]
    status: str
    s3_output_uri: Optional[str]
    metadata_info: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
