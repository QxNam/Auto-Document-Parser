from enum import Enum
from pydantic import BaseModel

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class MetadataMessage(BaseModel):
    metadata_id: str
    s3_uri: str
    status: ProcessingStatus
    time: int
    file_size: int
    file_name: str

    def to_dict(self):
        return self.model_dump()
    
