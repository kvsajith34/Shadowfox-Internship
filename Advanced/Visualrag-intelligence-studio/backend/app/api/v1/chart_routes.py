"""Chart analysis endpoint."""
from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional
from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.chart_service import chart_service
from app.utils.id_utils import generate_analysis_id
from app.utils.response_utils import success_response, error_response
from app.database.db import get_db
from app.database.crud import create_analysis_record

router = APIRouter()
logger = get_logger(__name__)


@router.post("/analyze-chart")
async def analyze_chart(
    file: UploadFile = File(...),
    question: Optional[str] = Form(""),
    db=Depends(get_db),
):
    """Analyze a chart or graph image."""
    try:
        file_content = await file.read()
        result = chart_service.analyze(file_content, file.filename or "chart.png", question=question or "")

        # chart_service reports which provider ACTUALLY produced the result
        # (may differ from requested if it fell back to mock).
        provider = result.pop("_effective_provider", "mock")

        # Save analysis record
        try:
            create_analysis_record(db, {
                "id": generate_analysis_id("chart"),
                "task_type": "chart",
                "question": question or "analyze_chart",
                "answer": result.get("answer", ""),
                "provider": provider,
                "safety_status": "passed",
                "confidence_score": result.get("confidence_score", 0.0),
                "hallucination_risk": "low",
                "result_json": result,
            })
        except Exception as e:
            logger.warning("DB save failed: %s", e)

        return success_response(
            message="Chart analyzed successfully",
            data=result,
            mock_mode=settings.MOCK_MODE,
            provider=provider,
        )

    except Exception as e:
        logger.error("Chart analysis failed: %s", type(e).__name__)
        return error_response(
            message="Chart analysis failed. The request could not be processed.",
            mock_mode=settings.MOCK_MODE,
            provider="mock",
        )
