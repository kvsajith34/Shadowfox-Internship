"""Visual chat endpoint."""
from fastapi import APIRouter, Depends
from app.schemas.chat_schema import VisualChatRequest
from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.provider_router import call_provider_method
from app.utils.response_utils import success_response, error_response
from app.database.db import get_db
from app.database.crud import create_analysis_record
from app.utils.id_utils import generate_analysis_id

router = APIRouter()
logger = get_logger(__name__)


@router.post("/visual-chat")
async def visual_chat(request: VisualChatRequest, db=Depends(get_db)):
    """Process a visual chat message."""
    try:
        # Fetch file metadata so providers/mock can vary responses by file
        filename  = None
        file_type = None
        file_path = None
        metadata  = None
        try:
            if request.file_id:
                from app.database.crud import get_file_record
                rec = get_file_record(db, request.file_id)
                if rec:
                    filename  = rec.filename
                    file_type = rec.file_type
                    file_path = rec.storage_path
                    metadata  = {"size_bytes": rec.size_bytes, **(rec.metadata_json or {})}
        except Exception as e:
            logger.debug("File record lookup skipped: %s", e)

        # Single safe call: resolves provider, calls it with the standardized
        # keyword-only interface, and falls back to mock on any failure
        # (including a method signature mismatch) — never raises.
        result, provider = call_provider_method(
            "visual_chat",
            provider_hint=request.provider,
            message=request.message,
            file_id=request.file_id,
            file_path=file_path,
            filename=filename,
            file_type=file_type,
            metadata=metadata,
            history=[h.model_dump() for h in request.history] if request.history else [],
        )

        # Save analysis record
        try:
            create_analysis_record(db, {
                "id": generate_analysis_id("visual_chat"),
                "file_id": request.file_id,
                "task_type": "visual_chat",
                "question": request.message,
                "answer": result.get("answer", ""),
                "provider": provider,
                "safety_status": "passed" if result.get("hallucination_risk") != "high" else "flagged",
                "confidence_score": result.get("confidence_score", 0.0),
                "hallucination_risk": result.get("hallucination_risk", "low"),
                "result_json": result,
            })
        except Exception as e:
            logger.warning("DB save failed: %s", e)

        return success_response(
            message="Visual chat response generated",
            data=result,
            mock_mode=settings.MOCK_MODE,
            provider=provider,
        )

    except Exception as e:
        logger.error("Visual chat failed: %s", type(e).__name__)
        return error_response(
            message="Visual chat failed. The request could not be processed.",
            mock_mode=settings.MOCK_MODE,
            provider="mock",
        )
