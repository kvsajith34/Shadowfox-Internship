"""Evaluation endpoint."""
from fastapi import APIRouter, Depends
from app.schemas.evaluation_schema import EvaluationRequest
from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.evaluation_service import evaluation_service
from app.utils.response_utils import success_response, error_response
from app.database.db import get_db
from app.database.crud import create_analysis_record
from app.utils.id_utils import generate_analysis_id

router = APIRouter()
logger = get_logger(__name__)


@router.post("/evaluate")
async def evaluate(request: EvaluationRequest, db=Depends(get_db)):
    """Evaluate an AI answer on quality dimensions."""
    try:
        result = evaluation_service.evaluate(
            question=request.question,
            answer=request.answer,
            evidence=request.evidence,
            task_type=request.task_type,
            provider_hint=request.provider,
        )

        # evaluation_service reports which provider ACTUALLY produced the
        # result (may differ from requested if it fell back to mock).
        provider = result.pop("_effective_provider", "mock")

        # Save analysis record
        try:
            create_analysis_record(db, {
                "id": generate_analysis_id("evaluation"),
                "task_type": "evaluation",
                "question": request.question,
                "answer": request.answer[:500],
                "provider": provider,
                "safety_status": "passed" if result.get("safety_score", 1.0) > 0.7 else "flagged",
                "confidence_score": result.get("relevance_score", 0.0),
                "hallucination_risk": result.get("hallucination_risk", "low"),
                "faithfulness_score": result.get("faithfulness_score", 0.0),
                "relevance_score": result.get("relevance_score", 0.0),
                "result_json": result,
            })
        except Exception as e:
            logger.warning("DB save failed: %s", e)

        return success_response(
            message="Evaluation complete",
            data=result,
            mock_mode=settings.MOCK_MODE,
            provider=provider,
        )

    except Exception as e:
        logger.error("Evaluation failed: %s", type(e).__name__)
        return error_response(
            message="Evaluation failed. The request could not be processed.",
            mock_mode=settings.MOCK_MODE,
            provider="mock",
        )
