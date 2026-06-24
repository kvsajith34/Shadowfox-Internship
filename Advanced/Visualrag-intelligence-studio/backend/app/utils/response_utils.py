"""Response utility functions."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def make_response(
    success: bool = True,
    message: str = "",
    data: Any = None,
    mock_mode: bool = True,
    provider: str = "mock",
) -> Dict[str, Any]:
    """Create a standardized API response.

    Every response includes a unique `request_id` (UUID4). The frontend uses
    this to discard stale responses when a new request was sent before the
    previous one completed — preventing old OpenAI/Gemini answers from
    appearing after the user switched providers or asked a new question.
    """
    return {
        "success": success,
        "message": message,
        "data": data,
        "mock_mode": mock_mode,
        "provider": provider,
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def success_response(
    message: str = "Success",
    data: Any = None,
    mock_mode: bool = True,
    provider: str = "mock",
) -> Dict[str, Any]:
    """Create a success response."""
    return make_response(True, message, data, mock_mode, provider)


def error_response(
    message: str = "Error",
    data: Any = None,
    mock_mode: bool = True,
    provider: str = "mock",
) -> Dict[str, Any]:
    """Create an error response."""
    return make_response(False, message, data, mock_mode, provider)
