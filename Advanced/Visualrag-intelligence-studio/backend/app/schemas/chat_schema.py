"""Visual chat request/response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class VisualChatRequest(BaseModel):
    file_id: Optional[str] = None
    message: str
    provider: str = "mock"
    history: List[ChatMessage] = []


class VisualChatResponseData(BaseModel):
    answer: str
    evidence: List[str] = []
    evaluation: Dict[str, Any] = {}
    confidence_score: float = 0.0
    safety_notes: str = ""
    hallucination_risk: str = "low"
    suggested_followups: List[str] = []
