"""ID generation utilities."""
import hashlib
import secrets
from typing import Optional


def generate_file_id(filename: str) -> str:
    """Generate a unique file ID."""
    salt = secrets.token_hex(8)
    raw = f"{filename}-{salt}"
    return f"file_{hashlib.sha256(raw.encode()).hexdigest()[:12]}"


def generate_analysis_id(task_type: str) -> str:
    """Generate a unique analysis ID."""
    salt = secrets.token_hex(6)
    return f"{task_type}_{hashlib.sha256(salt.encode()).hexdigest()[:10]}"


def generate_chunk_id(doc_id: str, chunk_index: int) -> str:
    """Generate a chunk ID for vector storage."""
    return f"{doc_id}_chunk_{chunk_index}"
