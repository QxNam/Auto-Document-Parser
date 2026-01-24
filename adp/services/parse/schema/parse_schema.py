from datetime import datetime
from typing import Dict
from pydantic import BaseModel


class ParsedResult(BaseModel):
    text: str
    metadata: Dict
    file_info: Dict
    processed_time: float
    processed_at: datetime = datetime.utcnow()
    