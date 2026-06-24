"""Chart analysis service."""
from typing import Any, Dict, Optional
from app.services.provider_router import call_provider_method
from app.services.document_parser import document_parser
from app.services.image_service import image_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ChartService:
    """Service for chart and graph analysis."""

    def analyze(
        self,
        file_content: bytes,
        filename: str,
        question: str = "",
        provider_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze a chart image or file."""
        # Extract text if it's a document (unlikely for charts, but handle it)
        extracted_text = ""
        if filename.lower().endswith(".pdf"):
            parsed = document_parser.parse_pdf(file_content)
            extracted_text = parsed.get("text", "")

        # Get image metadata
        img_meta: Dict[str, Any] = {}
        if image_service.is_image(filename):
            img_meta = image_service.get_metadata(file_content, filename) or {}

        metadata = {"size_bytes": len(file_content), **img_meta}

        result, provider = call_provider_method(
            "analyze_chart",
            provider_hint=provider_hint,
            question=question,
            filename=filename,
            file_type=filename.split(".")[-1].lower() if "." in filename else None,
            extracted_text=extracted_text,
            metadata=metadata,
        )

        if img_meta:
            result["image_metadata"] = img_meta
        result["_effective_provider"] = provider
        return result


# Singleton
chart_service = ChartService()
