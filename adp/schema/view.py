from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class ParsedPage(BaseModel):
    page: int
    text: str
    blocks: Optional[List[Dict[str, Any]]] = None

class ViewResponse(BaseModel):
    filename: str
    mime_type: str
    pages: int
    content: List[ParsedPage]
    meta: Dict[str, Any] = {}

