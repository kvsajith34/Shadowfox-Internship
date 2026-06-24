"""Evaluation service for answer quality assessment."""
from typing import Any, Dict, List, Optional
from app.services.provider_router import call_provider_method
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class EvaluationService:
    """Service for evaluating AI-generated answers."""

    def evaluate(
        self,
        question: str,
        answer: str,
        evidence: List[str],
        task_type: str = "visual_chat",
        provider_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate an AI answer on multiple quality dimensions."""
        result, provider = call_provider_method(
            "evaluate_answer",
            provider_hint=provider_hint,
            question=question,
            answer=answer,
            evidence=evidence,
            task_type=task_type,
        )
        result["_effective_provider"] = provider
        return result


# Singleton
evaluation_service = EvaluationService()
