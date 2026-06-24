"""Settings endpoints — GET/POST /api/v1/settings, GET /api/v1/provider-debug."""
from typing import Any, Dict, Optional, Tuple

from fastapi import APIRouter, Depends

from app.core.config import settings, env_file_exists, get_mock_mode_raw, get_default_model_for
from app.core.logging_config import get_logger
from app.database.db import get_db
from app.database.crud import get_current_settings, update_settings, reset_settings_to_env
from app.schemas.settings_schema import SettingsRequest
from app.services.provider_router import (
    set_runtime_provider,
    get_provider_with_reason,
    check_sdk_available,
    check_service_methods,
    get_last_fallback_info,
)
from app.utils.response_utils import success_response

router = APIRouter()
logger = get_logger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

DEFAULT_SETTINGS: Dict[str, Any] = {
    "selected_provider": "mock",
    "active_provider": "mock",
    "default_provider": "mock",
    "default_model": "mock-visualrag",
    "selected_model": "mock-visualrag",
    "vision_model": "gemini-1.5-flash",
    "chunk_size": 512,
    "similarity_threshold": 0.7,
    "mock_mode": True,
    "storage_backend": "local",
    "evaluation_sensitivity": 0.5,
    "api_key_status": {
        "openai": False,
        "gemini": False,
        "huggingface": False,
        "anthropic": False,
    },
    "fallback_reason": None,
    "debug_safe_config": {},
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _api_key_status() -> Dict[str, bool]:
    """Return which providers currently have an API key configured."""
    return {
        "openai": bool(settings.OPENAI_API_KEY),
        "gemini": bool(settings.GOOGLE_API_KEY),
        "huggingface": bool(settings.HF_TOKEN),
        "anthropic": bool(settings.CLAUDE_API_KEY),
    }


def _debug_safe_config() -> Dict[str, Any]:
    """Booleans and short strings only — never returns actual key values."""
    return {
        "env_loaded": env_file_exists(),
        "mock_mode_raw": get_mock_mode_raw(),
        "mock_mode_parsed": settings.MOCK_MODE,
        "openai_key_present": bool(settings.OPENAI_API_KEY),
        "gemini_key_present": bool(settings.GOOGLE_API_KEY),
        "hf_token_present": bool(settings.HF_TOKEN),
    }


def _compute_active_provider(selected: str, mock_mode: bool) -> Tuple[str, Optional[str]]:
    """Return (active_provider, fallback_reason).

    `mock_mode` here is the SAVED/UI value (from DB or this request) — it is
    the runtime source of truth and intentionally overrides the static .env
    MOCK_MODE once saved. .env only seeds the initial value of a brand-new
    settings row (see crud.get_current_settings) and is the target of
    "reset to environment defaults". This means toggling Mock Mode off in
    Settings reliably activates a real provider when its key is present —
    it is never silently re-overridden back to mock by .env.
    """
    if mock_mode or selected == "mock":
        return "mock", None

    has_key = _api_key_status().get(selected, False)
    if not has_key:
        return "mock", (
            f"Selected provider saved. Runtime is using Mock Mode because "
            f"the {selected} API key is not configured."
        )

    if not check_sdk_available(selected):
        return "mock", (
            f"Selected provider saved. Runtime is using Mock Mode because "
            f"the {selected} SDK package is not installed."
        )

    return selected, None


def _build_response(record, evaluation_sensitivity: float = 0.5) -> Dict[str, Any]:
    """Build the full settings response dict from a SettingsRecord."""
    mock_mode = bool(record.mock_mode)
    selected = record.default_provider or "mock"
    model = record.default_model or get_default_model_for(selected)
    active, fallback_reason = _compute_active_provider(selected, mock_mode)

    return {
        "selected_provider": selected,
        "active_provider": active,
        "default_provider": selected,   # backward compat alias
        "default_model": model,
        "selected_model": model,
        "vision_model": record.vision_model or "gemini-1.5-flash",
        "chunk_size": record.chunk_size or 512,
        "similarity_threshold": float(record.similarity_threshold or 0.7),
        "mock_mode": mock_mode,
        "storage_backend": record.storage_backend or "local",
        "evaluation_sensitivity": evaluation_sensitivity,
        "api_key_status": _api_key_status(),
        "fallback_reason": fallback_reason,
        "debug_safe_config": _debug_safe_config(),
    }


def _build_default_response(overrides: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Fallback response when DB is not yet ready."""
    base = dict(DEFAULT_SETTINGS)
    base["api_key_status"] = _api_key_status()
    base["debug_safe_config"] = _debug_safe_config()
    base.update(overrides)
    if "default_model" in overrides and "selected_model" not in overrides:
        base["selected_model"] = overrides["default_model"]
    active, reason = _compute_active_provider(base["selected_provider"], base["mock_mode"])
    base["active_provider"] = active
    base["fallback_reason"] = reason
    return base


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("/settings")
async def get_settings(db=Depends(get_db)):
    """Return current settings with computed provider status."""
    try:
        record = get_current_settings(db)
        data = _build_response(record)
        return success_response(
            message="Settings retrieved",
            data=data,
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )
    except Exception as e:
        logger.warning("Settings DB error on GET: %s", e)
        return success_response(
            message="Settings retrieved (initializing)",
            data=_build_default_response(),
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )


@router.post("/settings")
async def save_settings(request: SettingsRequest, db=Depends(get_db)):
    """Persist settings and update the in-memory provider runtime state."""
    try:
        if request.reset_to_env:
            record = reset_settings_to_env(db)
            data = _build_response(record, evaluation_sensitivity=request.evaluation_sensitivity or 0.5)
            set_runtime_provider(provider=data["selected_provider"], mock_mode=data["mock_mode"])
            return success_response(
                message=(
                    f"Settings reset to .env defaults — provider: {data['selected_provider']}, "
                    f"mock_mode: {data['mock_mode']}"
                ),
                data=data,
                mock_mode=settings.MOCK_MODE,
                provider=settings.DEFAULT_PROVIDER,
            )

        # Fields to write to DB (exclude evaluation_sensitivity/reset_to_env — no DB column)
        db_fields = {
            k: v for k, v in request.dict().items()
            if v is not None and k not in ("evaluation_sensitivity", "reset_to_env")
        }
        eval_sens = request.evaluation_sensitivity or 0.5

        if db_fields:
            record = update_settings(db, db_fields)
        else:
            record = get_current_settings(db)

        data = _build_response(record, evaluation_sensitivity=eval_sens)

        # Push new provider/mock_mode into in-memory runtime state so that
        # subsequent AI calls pick up the change without a server restart.
        set_runtime_provider(
            provider=data["selected_provider"],
            mock_mode=data["mock_mode"],
        )

        msg = "Settings saved"
        if data["fallback_reason"]:
            # Keep the toast short — full detail is shown in the UI panel
            msg = f"Settings saved — active provider: {data['active_provider']} (mock runtime)"

        return success_response(
            message=msg,
            data=data,
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )

    except Exception as e:
        logger.warning("Settings DB error on POST: %s", e)
        # Build best-effort response from request values
        overrides: Dict[str, Any] = {
            k: v for k, v in request.dict().items() if v is not None
        }
        if "default_provider" in overrides:
            overrides["selected_provider"] = overrides["default_provider"]
        data = _build_default_response(overrides)

        # Still update runtime state even if DB failed
        set_runtime_provider(
            provider=data["selected_provider"],
            mock_mode=data["mock_mode"],
        )

        msg = "Settings saved (in-memory only)"
        if data["fallback_reason"]:
            msg += f" — active provider: {data['active_provider']} (mock runtime)"

        return success_response(
            message=msg,
            data=data,
            mock_mode=settings.MOCK_MODE,
            provider=settings.DEFAULT_PROVIDER,
        )


@router.get("/provider-debug")
async def provider_debug(db=Depends(get_db)):
    """Safe, secret-free debug snapshot of provider resolution state.

    Returns only booleans and short categorical strings — never an actual
    API key value. Useful for diagnosing "why is this still in mock mode"
    without needing to read server logs or .env directly.
    """
    try:
        record = get_current_settings(db)
        selected = record.default_provider or "mock"
        model = record.default_model or get_default_model_for(selected)
        mock_mode = bool(record.mock_mode)
    except Exception as e:
        logger.warning("provider-debug: DB unavailable, using env: %s", e)
        selected = settings.DEFAULT_PROVIDER if settings.DEFAULT_PROVIDER in (
            "mock", "openai", "gemini", "huggingface", "anthropic"
        ) else "mock"
        model = get_default_model_for(selected)
        mock_mode = settings.MOCK_MODE

    active, fallback_reason = _compute_active_provider(selected, mock_mode)

    # Cross-check against the actual AI-call resolution path (mock_mode/key/
    # SDK gating only — NOT past live-call failures, which are intentionally
    # request-scoped and never pin future requests to mock).
    runtime_provider, runtime_reason = get_provider_with_reason(None if mock_mode else selected)
    if runtime_provider == "mock" and runtime_reason and active != "mock":
        active, fallback_reason = "mock", runtime_reason

    # Most recently OBSERVED live-call failure for the selected provider —
    # purely informational (does not affect active_provider above). Useful
    # for diagnosing "Gemini worked a minute ago but just failed once".
    last_reason, last_error_type = get_last_fallback_info(selected)

    data = {
        "env_loaded": env_file_exists(),
        "mock_mode_raw": get_mock_mode_raw(),
        "mock_mode_parsed": settings.MOCK_MODE,
        "default_provider": settings.DEFAULT_PROVIDER,
        "selected_provider": selected,
        "active_provider": active,
        "selected_model": model,
        "api_key_status": _api_key_status(),
        "fallback_reason": fallback_reason,
        "last_fallback_reason": last_reason,
        "last_provider_error_type": last_error_type,
        "provider_service_available": {
            "openai": check_sdk_available("openai"),
            "gemini": check_sdk_available("gemini"),
            "huggingface": check_sdk_available("huggingface"),
            "anthropic": check_sdk_available("anthropic"),
        },
        "service_methods_available": {
            "openai_visual_chat": check_service_methods("openai").get("visual_chat", False),
            "gemini_visual_chat": check_service_methods("gemini").get("visual_chat", False),
            "huggingface_visual_chat": check_service_methods("huggingface").get("visual_chat", False),
            "mock_visual_chat": check_service_methods("mock").get("visual_chat", False),
        },
    }

    return success_response(
        message="Provider debug snapshot",
        data=data,
        mock_mode=settings.MOCK_MODE,
        provider=settings.DEFAULT_PROVIDER,
    )
