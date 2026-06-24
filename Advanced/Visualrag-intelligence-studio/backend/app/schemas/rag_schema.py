"""RAG query request/response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class RagQueryRequest(BaseModel):
    file_id: str
    question: str
    provider: str = "mock"
    use_rag: bool = True


class RagQueryResponseData(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    retrieved_chunks: List[Dict[str, Any]] = []
    faithfulness_score: float = 0.0
    relevance_score: float = 0.0
    direct_llm_comparison: str = ""
    rag_grounded_answer: str = ""
    hallucination_risk: str = "low"
