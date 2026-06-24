"""Health check endpoint."""
from fastapi import APIRouter
from app.core.config import settings
from app.utils.response_utils import success_response

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health and configuration status."""
    data = {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "mock_mode": settings.MOCK_MODE,
        "default_provider": settings.DEFAULT_PROVIDER,
        "providers": {
            "mock": True,
            "openai": bool(settings.OPENAI_API_KEY),
            "gemini": bool(settings.GOOGLE_API_KEY),
            "anthropic": bool(settings.CLAUDE_API_KEY),
            "huggingface": bool(settings.HF_TOKEN),
        },
        "version": "1.0.0",
    }
    return success_response(
        message="VisualRAG Intelligence Studio is running",
        data=data,
        mock_mode=settings.MOCK_MODE,
        provider=settings.DEFAULT_PROVIDER,
    )
