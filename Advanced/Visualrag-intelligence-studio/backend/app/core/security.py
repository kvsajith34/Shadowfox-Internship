"""Security utilities."""
import hashlib
import os
import re
import secrets
from typing import Optional


def generate_file_id(filename: str) -> str:
    """Generate a unique file ID based on filename and random salt."""
    salt = secrets.token_hex(8)
    raw = f"{filename}-{salt}"
    return f"file_{hashlib.sha256(raw.encode()).hexdigest()[:12]}"


def generate_analysis_id(task_type: str) -> str:
    """Generate a unique analysis ID."""
    salt = secrets.token_hex(6)
    return f"{task_type}_{hashlib.sha256(salt.encode()).hexdigest()[:10]}"


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal."""
    filename = os.path.basename(filename)
    filename = re.sub(r"[^\w\.\-]", "_", filename)
    return filename


def mask_api_key(key: Optional[str]) -> str:
    """Mask an API key for safe display."""
    if not key:
        return "***not_set***"
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"
