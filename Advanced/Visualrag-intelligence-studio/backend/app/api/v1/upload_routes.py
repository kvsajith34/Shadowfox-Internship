"""Upload endpoint."""
from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.core.config import settings
from app.core.logging_config import get_logger
from app.utils.response_utils import success_response, error_response
from app.utils.id_utils import generate_file_id
from app.utils.file_utils import is_allowed_file, get_file_type, generate_safe_filename
from app.services.storage_service import storage_service
from app.services.document_parser import document_parser
from app.services.image_service import image_service
from app.database.db import get_db
from app.database.crud import create_file_record

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    analysisType: str = Form("general"),
    db=Depends(get_db),
):
    """Upload and analyze a file."""
    if not file.filename or not is_allowed_file(file.filename):
        return error_response(
            message=f"File type not allowed. Supported: .pdf, .png, .jpg, .jpeg, .txt, .csv",
            data={"filename": file.filename},
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )

    try:
        file_content = await file.read()
        size_bytes = len(file_content)
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024

        if size_bytes > max_bytes:
            return error_response(
                message=f"File too large. Max {settings.MAX_UPLOAD_MB}MB",
                mock_mode=settings.MOCK_MODE,
                provider=settings.DEFAULT_PROVIDER,
            )

        file_id = generate_file_id(file.filename)
        file_type = get_file_type(file.filename)
        safe_name = generate_safe_filename(file.filename)
        storage_path = f"{file_id}/{safe_name}"

        # Save to storage
        storage_service.save_file(file_content, storage_path)

        # Parse document for metadata
        summary = ""
        metadata = {"original_filename": file.filename}

        if file_type == "pdf":
            parsed = document_parser.parse_pdf(file_content)
            summary = parsed["text"][:200] + "..." if parsed["text"] else "PDF uploaded successfully"
            metadata["page_count"] = parsed.get("page_count", 0)
            metadata["char_count"] = parsed.get("metadata", {}).get("char_count", 0)
        elif file_type == "image":
            img_meta = image_service.get_metadata(file_content, file.filename)
            summary = f"Image: {img_meta.get('size', {}).get('width', '?')}x{img_meta.get('size', {}).get('height', '?')} {file.filename}"
            metadata.update(img_meta)
        elif file_type in ("text", "csv"):
            parsed = document_parser.parse(file_content, file.filename)
            summary = parsed["text"][:200] + "..." if parsed["text"] else "File uploaded"
            metadata.update(parsed.get("metadata", {}))

        # Suggested actions based on analysis type
        next_actions = {
            "general": ["visual-chat", "rag-query"],
            "invoice": ["extract-invoice"],
            "chart": ["analyze-chart"],
            "visual_chat": ["visual-chat"],
            "rag": ["pdf-rag-query"],
        }

        # Save to database
        try:
            create_file_record(db, {
                "id": file_id,
                "filename": file.filename,
                "file_type": file_type,
                "size_bytes": size_bytes,
                "storage_path": storage_path,
                "analysis_type": analysisType,
                "status": "uploaded",
                "summary": summary,
                "metadata_json": metadata,
                "provider": settings.DEFAULT_PROVIDER,
            })
        except Exception as e:
            logger.warning("DB save failed, continuing: %s", e)

        data = {
            "file_id": file_id,
            "filename": file.filename,
            "file_type": file_type,
            "size_bytes": size_bytes,
            "storage_path": storage_path,
            "analysis_type": analysisType,
            "status": "uploaded",
            "summary": summary,
            "metadata": metadata,
            "next_suggested_actions": next_actions.get(analysisType, ["visual-chat"]),
        }

        return success_response(
            message="File uploaded successfully",
            data=data,
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )

    except Exception as e:
        logger.error("Upload failed: %s", e)
        return error_response(
            message=f"Upload failed: {str(e)}",
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )
