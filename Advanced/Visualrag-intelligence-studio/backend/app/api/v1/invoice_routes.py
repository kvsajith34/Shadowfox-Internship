"""Invoice extraction endpoint."""
from fastapi import APIRouter, UploadFile, File, Depends
from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.invoice_service import invoice_service
from app.utils.id_utils import generate_analysis_id
from app.utils.response_utils import success_response, error_response
from app.database.db import get_db
from app.database.crud import create_analysis_record

router = APIRouter()
logger = get_logger(__name__)


@router.post("/extract-invoice")
async def extract_invoice(file: UploadFile = File(...), db=Depends(get_db)):
    """Extract structured data from an invoice file."""
    try:
        file_content = await file.read()
        result = invoice_service.extract_from_file(file_content, file.filename or "invoice.pdf")

        # invoice_service reports which provider ACTUALLY produced the result
        # (may differ from requested if it fell back to mock).
        provider = result.pop("_effective_provider", "mock")

        # Save analysis record
        try:
            create_analysis_record(db, {
                "id": generate_analysis_id("invoice"),
                "task_type": "invoice",
                "question": "extract_invoice",
                "answer": str(result.get("total_amount", "")),
                "provider": provider,
                "safety_status": "passed",
                "confidence_score": result.get("confidence_score", 0.0),
                "hallucination_risk": "low",
                "result_json": result,
            })
        except Exception as e:
            logger.warning("DB save failed: %s", e)

        return success_response(
            message="Invoice extracted successfully",
            data=result,
            mock_mode=settings.MOCK_MODE,
            provider=provider,
        )

    except Exception as e:
        logger.error("Invoice extraction failed: %s", type(e).__name__)
        return error_response(
            message="Invoice extraction failed. The request could not be processed.",
            mock_mode=settings.MOCK_MODE,
            provider="mock",
        )
