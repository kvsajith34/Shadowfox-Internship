"""Provider router: selects the correct AI service and safely calls it.

This module is the single place responsible for:
  1. Resolving which provider should handle a request (mock / openai / gemini
     / huggingface / anthropic), based on saved settings, .env, and per-request
     hints.
  2. Constructing that provider's service.
  3. Safely calling a standardized method on it — and falling back to
     MockAIService (which never raises) on ANY failure, including a bad
     method signature, a missing SDK, or a failed live API call.

Concepts (kept distinct on purpose — see call_provider_method's return value):
  - selected_provider:  what the user/settings actually want (e.g. "gemini"),
                         regardless of whether it's currently reachable.
  - requested_provider: the per-request hint passed by the caller (may be
                         'mock' meaning "use saved settings", or an explicit
                         override like 'openai').
  - active_provider / response_provider: what ACTUALLY produced this specific
                         response. Equals selected_provider on success, or
                         'mock' if a fallback occurred.
  - fallback_provider:  always 'mock' — the safety net every request degrades
                         to on failure.

IMPORTANT: a failed live call falls back to mock for THAT REQUEST ONLY. It
never permanently pins saved settings to mock — the very next request tries
the real provider again. A "last fallback reason" cache is kept purely for
/provider-debug display, not as a circuit breaker.

All five AI services (mock + 4 real providers) expose the exact same method
signatures:
    visual_chat(message, file_id=None, file_path=None, filename=None,
                file_type=None, metadata=None, history=None, model=None, **kwargs)
    rag_query(question, file_id=None, chunks=None, file_path=None,
              filename=None, metadata=None, use_rag=True, model=None, **kwargs)
    extract_invoice(file_id=None, file_path=None, filename=None, file_type=None,
                     extracted_text=None, metadata=None, model=None, **kwargs)
    analyze_chart(question=None, file_id=None, file_path=None, filename=None,
                  file_type=None, metadata=None, model=None, **kwargs)
    evaluate_answer(question, answer, evidence=None, task_type=None,
                     model=None, **kwargs)

Callers should always invoke these via call_provider_method() (keyword
arguments only) rather than calling a service's method directly, so that any
failure is caught here and degrades gracefully to mock — never a raw 500.
Real-provider services should NOT catch-and-fallback internally; they should
let exceptions propagate so this module can classify them centrally and
report an honest response_provider.
"""
import importlib.util
from typing import Any, Dict, Optional, Tuple

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# ─── Runtime state ────────────────────────────────────────────────────────────
# In-memory mirror of the DB settings_records row.
# Populated at startup (from DB) and updated whenever the user saves Settings.
# This is the SINGLE SOURCE OF TRUTH for mock_mode/provider at request time —
# it intentionally takes priority over the static settings.MOCK_MODE env value
# once a user has saved a preference, so a saved mock_mode=False reliably
# activates a real provider and is never silently re-overridden by .env.
# .env only seeds the *initial* value (see crud.get_current_settings) and is
# the target of "reset to environment defaults".
_runtime_state: Dict[str, Any] = {
    "mock_mode": None,   # None → fall back to settings.MOCK_MODE env var
    "provider": None,    # None → fall back to settings.DEFAULT_PROVIDER env var
}

# Most recent observed (reason, error_type) per provider — PURELY
# INFORMATIONAL, surfaced via /provider-debug's last_fallback_reason /
# last_provider_error_type. Deliberately NEVER consulted to decide whether
# to attempt a provider again — a past failure must never permanently pin
# the app to mock (that was a real bug: one transient RateLimitError/NotFound
# used to lock the provider to mock until server restart).
_last_fallback_reason: Dict[str, str] = {}
_last_provider_error_type: Dict[str, str] = {}

# Provider name -> importable module name, used for a side-effect-free
# "is the SDK installed" check.
_SDK_MODULE_MAP = {
    "openai": "openai",
    "gemini": "google.generativeai",
    "huggingface": "huggingface_hub",
    "anthropic": "anthropic",
}

# Provider name -> the standardized method names every service exposes.
# Used by /provider-debug's service_methods_available introspection.
_STANDARD_METHODS = ("visual_chat", "rag_query", "extract_invoice", "analyze_chart", "evaluate_answer")


def set_runtime_provider(provider: str, mock_mode: bool) -> None:
    """Update in-memory state. Called by settings_routes.py on every save."""
    _runtime_state["provider"] = provider
    _runtime_state["mock_mode"] = mock_mode
    logger.info("Runtime provider updated: provider=%s mock_mode=%s", provider, mock_mode)


def load_runtime_state_from_db(db) -> None:
    """Restore saved Settings from DB into runtime state on server startup."""
    try:
        from app.database.crud import get_current_settings
        record = get_current_settings(db)
        _runtime_state["provider"] = record.default_provider
        _runtime_state["mock_mode"] = bool(record.mock_mode)
        logger.info(
            "Loaded saved provider from DB: provider=%s mock_mode=%s",
            record.default_provider,
            bool(record.mock_mode),
        )
    except Exception as e:
        logger.warning("Could not load saved settings from DB at startup: %s", e)


def get_effective_mock_mode() -> bool:
    """Return the effective mock_mode (runtime state > env config)."""
    if _runtime_state["mock_mode"] is not None:
        return bool(_runtime_state["mock_mode"])
    return settings.MOCK_MODE


def check_sdk_available(provider: str) -> bool:
    """Side-effect-free check: is the provider's SDK package installed?

    Uses importlib.util.find_spec instead of actually importing the module,
    so this is cheap and never raises on missing optional dependencies.
    """
    module_name = _SDK_MODULE_MAP.get(provider)
    if not module_name:
        return False
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def check_service_methods(provider: str) -> Dict[str, bool]:
    """Introspect whether a provider's service class exposes every standardized
    method. Pure introspection — never constructs the service, never touches
    API keys, so this is always safe to call regardless of key/SDK status.
    """
    class_map = {
        "mock": ("app.services.mock_ai_service", "MockAIService"),
        "openai": ("app.services.openai_service", "OpenAIService"),
        "gemini": ("app.services.gemini_service", "GeminiService"),
        "huggingface": ("app.services.huggingface_service", "HuggingFaceService"),
        "anthropic": ("app.services.anthropic_service", "AnthropicService"),
    }
    module_name, class_name = class_map.get(provider, (None, None))
    if not module_name:
        return {m: False for m in _STANDARD_METHODS}
    try:
        import importlib
        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name)
        return {m: callable(getattr(cls, m, None)) for m in _STANDARD_METHODS}
    except Exception:
        return {m: False for m in _STANDARD_METHODS}


def record_fallback_reason(provider: str, reason: str, error_type: Optional[str] = None) -> None:
    """Record why a real provider's call failed THIS TIME. Purely informational
    (surfaced via /provider-debug) — never used to gate future attempts.
    """
    _last_fallback_reason[provider] = reason
    if error_type:
        _last_provider_error_type[provider] = error_type
    logger.warning("Provider '%s' fallback recorded: %s (%s)", provider, reason, error_type or "n/a")


def clear_fallback_reason(provider: str) -> None:
    """Clear a previously recorded fallback reason once a provider succeeds again."""
    _last_fallback_reason.pop(provider, None)
    _last_provider_error_type.pop(provider, None)


def get_last_fallback_info(provider: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """Most recent (reason, error_type) for a provider, for /provider-debug.

    If `provider` is None, returns the most recently recorded entry across
    any provider (or (None, None) if nothing has ever failed). Purely
    informational — does not affect routing decisions.
    """
    if provider:
        return _last_fallback_reason.get(provider), _last_provider_error_type.get(provider)
    for p, reason in _last_fallback_reason.items():
        return reason, _last_provider_error_type.get(p)
    return None, None


def _resolve_candidate(provider_hint: Optional[str]) -> str:
    """The provider the user/settings actually want, BEFORE any mock_mode,
    key-presence, or SDK-availability gating is applied. This is what
    'selected_provider' reflects even when the final active provider is
    forced to mock.
    """
    if provider_hint and provider_hint not in ("mock", "auto", ""):
        return provider_hint
    return _runtime_state.get("provider") or settings.DEFAULT_PROVIDER


def get_provider_with_reason(provider_hint: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """Resolve the effective AI provider for a request, plus a safe reason
    when the result is a (pre-call) fallback to mock.

    Reason values (never include secrets or raw exception messages):
      - "mock mode enabled"                 — MOCK_MODE/mock_mode is on
      - "selected provider API key missing" — key not configured
      - "provider SDK error"                — package not installed

    A failed LIVE call is classified separately by call_provider_method()
    (see _classify_provider_error) and is NOT consulted here — every request
    gets a fresh attempt at the real provider; only mock_mode/key/SDK gating
    short-circuits before even trying.
    """
    effective_mock = get_effective_mock_mode()
    candidate = _resolve_candidate(provider_hint)

    if effective_mock:
        return "mock", "mock mode enabled"

    if candidate == "mock" or not candidate:
        return "mock", None

    key_present = {
        "openai": bool(settings.OPENAI_API_KEY),
        "gemini": bool(settings.GOOGLE_API_KEY),
        "anthropic": bool(settings.CLAUDE_API_KEY),
        "huggingface": bool(settings.HF_TOKEN),
    }.get(candidate, False)

    if not key_present:
        return "mock", "selected provider API key missing"

    if not check_sdk_available(candidate):
        return "mock", "provider SDK error"

    return candidate, None


def get_provider(provider_hint: Optional[str] = None) -> str:
    """Determine the effective AI provider for a request (provider name only)."""
    provider, _ = get_provider_with_reason(provider_hint)
    return provider


def _construct_service(provider: str):
    """Construct a real provider's service instance. Raises on failure —
    callers are responsible for catching and falling back to mock.
    """
    if provider == "openai":
        from app.services.openai_service import OpenAIService
        return OpenAIService()
    elif provider == "gemini":
        from app.services.gemini_service import GeminiService
        return GeminiService()
    elif provider == "anthropic":
        from app.services.anthropic_service import AnthropicService
        return AnthropicService()
    elif provider == "huggingface":
        from app.services.huggingface_service import HuggingFaceService
        return HuggingFaceService()
    else:
        from app.services.mock_ai_service import MockAIService
        return MockAIService()


def get_ai_service(provider_hint: Optional[str] = None):
    """Get a constructed AI service instance for the resolved provider.

    Falls back to MockAIService if construction fails (missing SDK, bad key,
    etc). Kept for callers that need a service instance directly. For a
    single method call with full method-call-time fallback protection,
    structured fallback info, and an honest response_provider, prefer
    call_provider_method() instead.
    """
    provider, _ = get_provider_with_reason(provider_hint)

    if provider == "mock":
        from app.services.mock_ai_service import MockAIService
        return MockAIService()

    try:
        svc = _construct_service(provider)
        clear_fallback_reason(provider)
        return svc
    except (ImportError, ModuleNotFoundError) as e:
        logger.warning("%s SDK import failed during construction", provider)
        record_fallback_reason(provider, "provider SDK error", type(e).__name__)
    except Exception as e:
        logger.warning("%s service initialization failed: %s", provider, type(e).__name__)
        record_fallback_reason(provider, "provider API request failed", type(e).__name__)

    from app.services.mock_ai_service import MockAIService
    return MockAIService()


# ─── Safe, provider-specific error classification ─────────────────────────────
# Maps a raised exception to (provider_error_type, safe_fallback_reason).
# provider_error_type is just the exception's class name — safe, never
# contains secrets. safe_fallback_reason is a short, friendly, actionable
# message safe to display directly in the UI. These string comparisons are
# based on the REAL exception class names raised by each SDK (openai.*,
# google.api_core.exceptions.*, huggingface_hub.*) — duck-typed via
# type(exc).__name__ so no hard import dependency on optional SDKs is needed
# just to classify an error.

def _classify_provider_error(provider: str, exc: Exception) -> Tuple[str, str]:
    error_type = type(exc).__name__

    if provider == "openai":
        if error_type == "RateLimitError":
            return error_type, "OpenAI rate limit or quota reached. Using mock fallback for this request."
        if error_type in ("AuthenticationError", "PermissionDeniedError"):
            return error_type, "OpenAI authentication failed. Check OPENAI_API_KEY in backend/.env. Using mock fallback."
        if error_type in ("NotFoundError",):
            return error_type, "OpenAI model not found. Check OPENAI_MODEL in backend/.env. Using mock fallback."
        if error_type in ("APIConnectionError", "APITimeoutError"):
            return error_type, "Could not reach OpenAI (network/connection issue). Using mock fallback."
        return error_type, "OpenAI request failed. Using mock fallback for this request."

    if provider == "gemini":
        if error_type == "NotFound":
            return error_type, "Gemini model not found or unavailable. Check GEMINI_MODEL in backend/.env. Using mock fallback."
        if error_type == "ResourceExhausted":
            return error_type, "Gemini rate limit or quota reached. Using mock fallback for this request."
        if error_type in ("PermissionDenied", "Unauthenticated"):
            return error_type, "Gemini authentication failed. Check GOOGLE_API_KEY in backend/.env. Using mock fallback."
        if error_type in ("DeadlineExceeded", "ServiceUnavailable"):
            return error_type, "Could not reach Gemini (network/connection issue). Using mock fallback."
        return error_type, "Gemini request failed. Using mock fallback for this request."

    if provider == "huggingface":
        return error_type, "Hugging Face provider failed or model unavailable. Using mock fallback."

    if provider == "anthropic":
        if error_type == "RateLimitError":
            return error_type, "Anthropic rate limit or quota reached. Using mock fallback for this request."
        if error_type == "AuthenticationError":
            return error_type, "Anthropic authentication failed. Check CLAUDE_API_KEY in backend/.env. Using mock fallback."
        return error_type, "Anthropic request failed. Using mock fallback for this request."

    return error_type, "Provider request failed. Using mock fallback for this request."


def call_provider_method(
    method_name: str,
    provider_hint: Optional[str] = None,
    **call_kwargs: Any,
) -> Tuple[Dict[str, Any], str]:
    """Centralized, safe entrypoint for calling any standardized AI service method.

    - Resolves the active provider via get_provider_with_reason().
    - If a real provider is active, constructs its service and calls
      getattr(service, method_name)(**call_kwargs) using ONLY keyword
      arguments (the standardized interface never relies on positional order).
    - On ANY failure — a TypeError from an unexpected/missing argument, a
      missing SDK, or a failed live API call (RateLimitError, NotFound, etc)
      — classifies the error, records it (informational only — does NOT pin
      future requests), and retries the exact same call against
      MockAIService, which is guaranteed never to raise. The fallback is
      scoped to THIS request only; saved settings are never modified.
    - Returns (result_dict, effective_provider). The result dict ALWAYS
      includes four extra keys for response transparency:
        selected_provider   — what the user/settings want (e.g. "gemini")
        response_provider   — what actually produced this answer
        fallback_reason      — short safe reason, or null on success
        provider_error_type  — raised exception's class name, or null

    Never exposes secrets: only exception TYPE names are logged/returned,
    never exception messages or argument values that could contain key
    fragments.
    """
    selected = _resolve_candidate(provider_hint)
    provider, pre_reason = get_provider_with_reason(provider_hint)

    if provider != "mock":
        try:
            service = _construct_service(provider)
            method = getattr(service, method_name)
            result = method(**call_kwargs)
            clear_fallback_reason(provider)
            result["selected_provider"] = selected
            result["response_provider"] = provider
            result["fallback_reason"] = None
            result["provider_error_type"] = None
            return result, provider
        except TypeError:
            logger.warning(
                "Provider '%s' method '%s' rejected the call arguments (signature mismatch)",
                provider, method_name,
            )
            error_type, safe_reason = "TypeError", "provider method signature error"
            record_fallback_reason(provider, safe_reason, error_type)
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning("Provider '%s' SDK error calling '%s'", provider, method_name)
            error_type, safe_reason = type(e).__name__, "provider SDK error"
            record_fallback_reason(provider, safe_reason, error_type)
        except Exception as e:
            error_type, safe_reason = _classify_provider_error(provider, e)
            logger.warning(
                "Provider '%s' API request failed calling '%s': %s", provider, method_name, error_type
            )
            record_fallback_reason(provider, safe_reason, error_type)

        from app.services.mock_ai_service import MockAIService
        result = getattr(MockAIService(), method_name)(**call_kwargs)
        result["selected_provider"] = selected
        result["response_provider"] = "mock"
        result["fallback_reason"] = safe_reason
        result["provider_error_type"] = error_type
        return result, "mock"

    # Provider resolved to mock BEFORE any call was attempted (mock mode is
    # on, the selected provider's key is missing, or its SDK isn't installed).
    from app.services.mock_ai_service import MockAIService
    result = getattr(MockAIService(), method_name)(**call_kwargs)
    result["selected_provider"] = selected
    result["response_provider"] = "mock"
    result["fallback_reason"] = pre_reason
    result["provider_error_type"] = None
    return result, "mock"
