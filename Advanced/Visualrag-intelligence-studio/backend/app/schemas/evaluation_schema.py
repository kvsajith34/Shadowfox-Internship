"""Evaluation request/response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    question: str
    answer: str
    evidence: List[str] = []
    task_type: str = "visual_chat"
    provider: str = "mock"


class EvaluationResponseData(BaseModel):
    relevance_score: float = 0.0
    faithfulness_score: float = 0.0
    completeness_score: float = 0.0
    safety_score: float = 0.0
    hallucination_risk: str = "low"
    missing_evidence: List[str] = []
    risk_explanation: str = ""
    improvement_suggestions: List[str] = []
