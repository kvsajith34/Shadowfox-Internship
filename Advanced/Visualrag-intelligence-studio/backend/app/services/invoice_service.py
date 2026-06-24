"""Invoice extraction service."""
from typing import Any, Dict, Optional
from app.services.provider_router import call_provider_method
from app.services.document_parser import document_parser
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class InvoiceService:
    """Service for invoice extraction."""

    def extract_from_file(
        self, file_content: bytes, filename: str, provider_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract invoice data from an uploaded file."""
        # Parse document text if it's a PDF
        extracted_text = ""
        if filename.lower().endswith(".pdf"):
            parsed = document_parser.parse_pdf(file_content)
            extracted_text = parsed.get("text", "")

        result, provider = call_provider_method(
            "extract_invoice",
            provider_hint=provider_hint,
            filename=filename,
            file_type=filename.split(".")[-1].lower() if "." in filename else None,
            extracted_text=extracted_text,
            metadata={"size_bytes": len(file_content)},
        )
        result["_effective_provider"] = provider
        return result

    def extract_from_file_id(self, file_id: str, provider_hint: Optional[str] = None) -> Dict[str, Any]:
        """Extract invoice data from a previously uploaded file (by ID only)."""
        result, provider = call_provider_method(
            "extract_invoice",
            provider_hint=provider_hint,
            file_id=file_id,
        )
        result["_effective_provider"] = provider
        return result


# Singleton
invoice_service = InvoiceService()
