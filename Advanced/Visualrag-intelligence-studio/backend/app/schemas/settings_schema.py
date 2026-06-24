"""Settings request/response schemas."""
from typing import Any, Dict, Optional
from pydantic import BaseModel


class SettingsRequest(BaseModel):
    """Fields accepted by POST /api/v1/settings.

    `default_provider` stores the user-selected provider (may differ from the
    active provider if the API key is missing).
    `evaluation_sensitivity` is accepted and returned but not persisted to the
    DB column set (handled via in-memory state to avoid migration issues).
    `reset_to_env`: when true, ignores all other fields and resets saved
    provider/model/mock_mode back to backend/.env defaults.
    """
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    vision_model: Optional[str] = None
    chunk_size: Optional[int] = None
    similarity_threshold: Optional[float] = None
    mock_mode: Optional[bool] = None
    storage_backend: Optional[str] = None
    evaluation_sensitivity: Optional[float] = None
    reset_to_env: Optional[bool] = False


class SettingsResponseData(BaseModel):
    """Full settings response returned to the frontend."""
    # User-chosen provider (what was saved)
    selected_provider: str = "mock"
    # Provider actually in use (falls back to mock if key missing / mock_mode on)
    active_provider: str = "mock"
    # Alias kept for backward compatibility with older frontend code
    default_provider: str = "mock"
    # Model name for the selected provider
    default_model: str = "mock-visualrag"
    selected_model: str = "mock-visualrag"
    vision_model: str = "gemini-1.5-flash"
    chunk_size: int = 512
    similarity_threshold: float = 0.7
    mock_mode: bool = True
    storage_backend: str = "local"
    evaluation_sensitivity: float = 0.5
    # Which providers have their API key configured (never exposes the key)
    api_key_status: Dict[str, bool] = {}
    # Short, human-readable reason when active_provider != selected_provider
    fallback_reason: Optional[str] = None
    # Booleans only — never contains actual key values
    debug_safe_config: Dict[str, Any] = {}
