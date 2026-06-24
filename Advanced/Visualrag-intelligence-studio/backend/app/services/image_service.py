"""Image service for metadata extraction and basic analysis."""
import io
import os
from typing import Dict, Any
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ImageService:
    """Handle image metadata and basic analysis."""

    def get_metadata(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract image metadata using Pillow."""
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(file_content))
            return {
                "format": img.format or os.path.splitext(filename)[1].upper().lstrip("."),
                "mode": img.mode,
                "size": {"width": img.width, "height": img.height},
                "filename": filename,
                "file_size_bytes": len(file_content),
                "aspect_ratio": round(img.width / img.height, 2) if img.height else 0,
            }
        except Exception as e:
            logger.warning("Image metadata extraction failed: %s", e)
            return {
                "format": os.path.splitext(filename)[1].upper().lstrip("."),
                "filename": filename,
                "file_size_bytes": len(file_content),
                "error": str(e),
            }

    def is_image(self, filename: str) -> bool:
        """Check if a filename is an image."""
        ext = os.path.splitext(filename)[1].lower()
        return ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")


# Singleton
image_service = ImageService()
