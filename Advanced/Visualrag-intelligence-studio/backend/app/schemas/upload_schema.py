"""Upload request/response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class UploadResponseData(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size_bytes: int
    storage_path: str
    analysis_type: str
    status: str
    summary: str
    metadata: Dict[str, Any] = {}
    next_suggested_actions: List[str] = []
