"""File utility functions."""
import os
import uuid
from typing import Optional


ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".csv"}
ALLOWED_MIMES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
    "text/csv",
    "application/vnd.ms-excel",
}


def get_file_extension(filename: str) -> str:
    """Get the lowercase file extension."""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def get_file_type(filename: str) -> str:
    """Determine the file type category."""
    ext = get_file_extension(filename)
    if ext == ".pdf":
        return "pdf"
    elif ext in (".png", ".jpg", ".jpeg"):
        return "image"
    elif ext == ".txt":
        return "text"
    elif ext == ".csv":
        return "csv"
    return "unknown"


def generate_safe_filename(filename: str) -> str:
    """Generate a safe, unique filename."""
    ext = get_file_extension(filename)
    safe_name = uuid.uuid4().hex[:12]
    return f"{safe_name}{ext}"


def format_file_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def ensure_directory(path: str) -> None:
    """Ensure a directory exists."""
    os.makedirs(path, exist_ok=True)
