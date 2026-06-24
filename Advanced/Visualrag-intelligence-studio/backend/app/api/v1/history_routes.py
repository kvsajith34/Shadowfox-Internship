"""History endpoint."""
from fastapi import APIRouter, Depends
from app.core.config import settings
from app.utils.response_utils import success_response, error_response
from app.database.db import get_db
from app.database.crud import list_analysis_records

router = APIRouter()


@router.get("/history")
async def get_history(db=Depends(get_db)):
    """Get recent analysis history."""
    try:
        records = list_analysis_records(db, limit=50)
        data = [
            {
                "id": r.id,
                "filename": r.file_id or "",
                "type": r.task_type,
                "provider": r.provider,
                "safety": r.safety_status,
                "created_at": r.created_at.isoformat() if r.created_at else "",
                "task_type": r.task_type,
                "summary": (r.answer[:100] + "...") if r.answer and len(r.answer) > 100 else (r.answer or ""),
            }
            for r in records
        ]
        return success_response(
            message="History retrieved",
            data=data,
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )
    except Exception as e:
        # Return empty history if DB not ready
        return success_response(
            message="History retrieved (initializing)",
            data=[],
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )
