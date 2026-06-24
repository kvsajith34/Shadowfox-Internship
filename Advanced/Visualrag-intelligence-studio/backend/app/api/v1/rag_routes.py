"""PDF RAG query endpoint."""
from fastapi import APIRouter, Depends
from app.schemas.rag_schema import RagQueryRequest
from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.rag_service import rag_service
from app.services.storage_service import storage_service
from app.database.db import get_db
from app.utils.id_utils import generate_analysis_id
from app.utils.response_utils import success_response, error_response

router = APIRouter()
logger = get_logger(__name__)


@router.post("/pdf-rag-query")
async def pdf_rag_query(request: RagQueryRequest, db=Depends(get_db)):
    """Process a PDF RAG query."""
    try:
        # Try to get file content from storage (non-fatal if unavailable)
        file_content = None
        filename = None
        try:
            from app.database.crud import get_file_record
            file_record = get_file_record(db, request.file_id)
            if file_record:
                filename = file_record.filename
                try:
                    file_content = storage_service.read_file(file_record.storage_path)
                except Exception:
                    pass
        except Exception:
            pass  # DB not ready — mock service handles it

        result = rag_service.query(
            file_id=request.file_id,
            question=request.question,
            use_rag=request.use_rag,
            provider_hint=request.provider,
            file_content=file_content,
            filename=filename,
        )

        # call_provider_method() reports which provider ACTUALLY produced the
        # result (may differ from the requested one if it fell back to mock).
        provider = result.pop("_effective_provider", "mock")

        # Save analysis record (non-fatal)
        try:
            from app.database.crud import create_analysis_record
            create_analysis_record(db, {
                "id": generate_analysis_id("rag"),
                "file_id": request.file_id,
                "task_type": "rag",
                "question": request.question,
                "answer": result.get("answer", ""),
                "provider": provider,
                "safety_status": "passed" if result.get("hallucination_risk") != "high" else "flagged",
                "confidence_score": 0.0,
                "hallucination_risk": result.get("hallucination_risk", "low"),
                "faithfulness_score": result.get("faithfulness_score", 0.0),
                "relevance_score": result.get("relevance_score", 0.0),
                "result_json": result,
            })
        except Exception as e:
            logger.warning("DB save failed: %s", e)

        return success_response(
            message="RAG query processed",
            data=result,
            mock_mode=settings.MOCK_MODE,
            provider=provider,
        )

    except Exception as e:
        logger.error("RAG query failed: %s", type(e).__name__)
        return error_response(
            message="RAG query failed. The request could not be processed.",
            mock_mode=settings.MOCK_MODE,
            provider="mock",
        )
