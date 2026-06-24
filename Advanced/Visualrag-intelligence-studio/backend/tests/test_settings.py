"""Tests for Settings persistence, provider activation, and debug endpoints.

Note: conftest.py sets MOCK_MODE=true in os.environ BEFORE the app (and the
module-level `settings` singleton) is imported, so `settings.MOCK_MODE` is
frozen to True for the whole test session — this matches every other test
file's baseline (mock mode is the safe default everywhere). Tests that need
to exercise "key present + mock_mode off" therefore:
  - construct a *fresh* Settings() instance to test env parsing in isolation, and
  - use monkeypatch to simulate API keys being present on the shared
    `settings` singleton, and
  - pass `mock_mode=False` as the per-request/saved value (which is exactly
    what the Settings page sends), since that is the actual override path —
    not the frozen env-level settings.MOCK_MODE.
"""
import os

from fastapi.testclient import TestClient

from app.core.config import Settings, settings as app_settings
from app.api.v1 import settings_routes
from app.api.v1.settings_routes import _compute_active_provider, _api_key_status, _debug_safe_config


# ─── 1. MOCK_MODE parsing ───────────────────────────────────────────────────────

def test_mock_mode_false_string_parses_as_false():
    """The classic bug: bool("false") == True. Must not happen here."""
    os.environ["MOCK_MODE"] = "false"
    try:
        s = Settings()
        assert s.MOCK_MODE is False
    finally:
        os.environ["MOCK_MODE"] = "true"  # restore test-session default


def test_mock_mode_true_string_parses_as_true():
    os.environ["MOCK_MODE"] = "true"
    s = Settings()
    assert s.MOCK_MODE is True


def test_mock_mode_various_falsy_strings():
    for raw in ["False", "FALSE", "0", "no", "off", "  false  "]:
        os.environ["MOCK_MODE"] = raw
        s = Settings()
        assert s.MOCK_MODE is False, f"Expected False for MOCK_MODE={raw!r}"
    os.environ["MOCK_MODE"] = "true"


def test_mock_mode_various_truthy_strings():
    for raw in ["True", "TRUE", "1", "yes", "on"]:
        os.environ["MOCK_MODE"] = raw
        s = Settings()
        assert s.MOCK_MODE is True, f"Expected True for MOCK_MODE={raw!r}"
    os.environ["MOCK_MODE"] = "true"


# ─── 2. API key alias resolution ────────────────────────────────────────────────

def test_gemini_api_key_alias_fills_google_api_key():
    os.environ["GOOGLE_API_KEY"] = ""
    os.environ["GEMINI_API_KEY"] = "fake-gemini-alias-key"
    try:
        s = Settings()
        assert s.GOOGLE_API_KEY == "fake-gemini-alias-key"
    finally:
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GOOGLE_API_KEY", None)


def test_huggingface_token_alias_fills_hf_token():
    os.environ["HF_TOKEN"] = ""
    os.environ["HUGGINGFACE_API_KEY"] = "fake-hf-alias-key"
    try:
        s = Settings()
        assert s.HF_TOKEN == "fake-hf-alias-key"
    finally:
        os.environ.pop("HUGGINGFACE_API_KEY", None)
        os.environ.pop("HF_TOKEN", None)


def test_primary_key_wins_over_alias_when_both_set():
    os.environ["GOOGLE_API_KEY"] = "primary-key"
    os.environ["GEMINI_API_KEY"] = "alias-key"
    try:
        s = Settings()
        assert s.GOOGLE_API_KEY == "primary-key"
    finally:
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GOOGLE_API_KEY", None)


# ─── 3. API key presence detection ──────────────────────────────────────────────

def test_api_key_status_reflects_configured_keys(monkeypatch):
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", None)
    monkeypatch.setattr(app_settings, "HF_TOKEN", "fake-hf-key")

    status = _api_key_status()
    assert status["openai"] is True
    assert status["gemini"] is False
    assert status["huggingface"] is True


# ─── 4. Provider activation logic ───────────────────────────────────────────────

def test_gemini_activates_when_key_present_and_mock_mode_off(monkeypatch):
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", "fake-gemini-key")
    # SDK availability is a separate concern (tested below); assume installed
    # here so this test isolates the key + mock_mode resolution logic, which
    # is the literal acceptance criterion: "selected Gemini with
    # GOOGLE_API_KEY and MOCK_MODE=false activates Gemini".
    monkeypatch.setattr(settings_routes, "check_sdk_available", lambda p: True)
    active, reason = _compute_active_provider("gemini", mock_mode=False)
    assert active == "gemini"
    assert reason is None


def test_openai_activates_when_key_present_and_mock_mode_off(monkeypatch):
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", "fake-openai-key")
    monkeypatch.setattr(settings_routes, "check_sdk_available", lambda p: True)
    active, reason = _compute_active_provider("openai", mock_mode=False)
    assert active == "openai"
    assert reason is None


def test_huggingface_activates_when_key_present_and_mock_mode_off(monkeypatch):
    monkeypatch.setattr(app_settings, "HF_TOKEN", "fake-hf-key")
    monkeypatch.setattr(settings_routes, "check_sdk_available", lambda p: True)
    active, reason = _compute_active_provider("huggingface", mock_mode=False)
    assert active == "huggingface"
    assert reason is None


def test_key_present_but_sdk_missing_falls_back_to_mock(monkeypatch):
    """Even with a valid key, an uninstalled SDK package must fall back safely."""
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", "fake-gemini-key")
    monkeypatch.setattr(settings_routes, "check_sdk_available", lambda p: False)
    active, reason = _compute_active_provider("gemini", mock_mode=False)
    assert active == "mock"
    assert reason is not None
    assert "sdk" in reason.lower() or "installed" in reason.lower()


def test_missing_key_falls_back_to_mock(monkeypatch):
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", None)
    active, reason = _compute_active_provider("openai", mock_mode=False)
    assert active == "mock"
    assert reason is not None
    assert "key" in reason.lower()


def test_mock_mode_true_always_returns_mock_even_with_key(monkeypatch):
    """Saved mock_mode=True must always win, regardless of key presence."""
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", "fake-gemini-key")
    active, reason = _compute_active_provider("gemini", mock_mode=True)
    assert active == "mock"
    assert reason is None


def test_selected_mock_returns_mock_with_no_reason():
    active, reason = _compute_active_provider("mock", mock_mode=False)
    assert active == "mock"
    assert reason is None


def test_fallback_reason_is_concise(monkeypatch):
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", None)
    _, reason = _compute_active_provider("openai", mock_mode=False)
    assert reason is not None
    assert len(reason) <= 200


# ─── 5. Settings persistence (DB round trip via API) ────────────────────────────

def test_settings_get_returns_required_fields(client: TestClient):
    r = client.get("/api/v1/settings")
    assert r.status_code == 200
    data = r.json()["data"]
    for field in [
        "selected_provider", "active_provider", "selected_model",
        "mock_mode", "api_key_status", "fallback_reason", "debug_safe_config",
    ]:
        assert field in data, f"Missing field: {field}"


def test_settings_post_persists_selected_provider(client: TestClient):
    r = client.post("/api/v1/settings", json={"default_provider": "gemini", "mock_mode": False})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["selected_provider"] == "gemini"

    # Persisted — a fresh GET reflects the same saved value
    r2 = client.get("/api/v1/settings")
    assert r2.json()["data"]["selected_provider"] == "gemini"

    # Reset back to mock for test isolation
    client.post("/api/v1/settings", json={"default_provider": "mock", "mock_mode": True})


def test_settings_post_no_key_falls_back_to_mock(client: TestClient):
    r = client.post("/api/v1/settings", json={"default_provider": "huggingface", "mock_mode": False})
    data = r.json()["data"]
    assert data["selected_provider"] == "huggingface"
    assert data["active_provider"] == "mock"
    assert data["fallback_reason"] is not None
    client.post("/api/v1/settings", json={"default_provider": "mock", "mock_mode": True})


def test_settings_reset_to_env(client: TestClient):
    client.post("/api/v1/settings", json={"default_provider": "openai", "mock_mode": False})
    r = client.post("/api/v1/settings", json={"reset_to_env": True})
    assert r.status_code == 200
    data = r.json()["data"]
    # In the test environment, .env defaults are mock/MOCK_MODE=true
    assert data["selected_provider"] == "mock"
    assert data["mock_mode"] is True


# ─── 6. No secrets ever appear in responses ─────────────────────────────────────

def test_no_secrets_in_settings_response(client: TestClient, monkeypatch):
    secret = "sk-THIS-IS-A-SECRET-KEY-VALUE-12345"
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", secret)
    r = client.get("/api/v1/settings")
    body_text = r.text
    assert secret not in body_text
    # api_key_status must only contain booleans
    status = r.json()["data"]["api_key_status"]
    assert all(isinstance(v, bool) for v in status.values())


def test_no_secrets_in_provider_debug_response(client: TestClient, monkeypatch):
    secret = "AIza-THIS-IS-A-SECRET-GEMINI-KEY"
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", secret)
    r = client.get("/api/v1/provider-debug")
    assert r.status_code == 200
    assert secret not in r.text


# ─── 7. Provider debug endpoint structure ───────────────────────────────────────

def test_provider_debug_endpoint_structure(client: TestClient):
    r = client.get("/api/v1/provider-debug")
    assert r.status_code == 200
    data = r.json()["data"]
    for field in [
        "env_loaded", "mock_mode_raw", "mock_mode_parsed", "default_provider",
        "selected_provider", "active_provider", "selected_model",
        "api_key_status", "fallback_reason", "provider_service_available",
    ]:
        assert field in data, f"Missing field: {field}"
    assert isinstance(data["mock_mode_parsed"], bool)
    assert isinstance(data["env_loaded"], bool)
    assert isinstance(data["provider_service_available"], dict)


def test_provider_debug_alias(client: TestClient):
    r = client.get("/provider-debug")
    assert r.status_code == 200
    assert r.json()["success"] is True


def test_debug_safe_config_has_no_actual_keys(monkeypatch):
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", "sk-secret-value")
    debug = _debug_safe_config()
    assert debug["openai_key_present"] is True
    assert "sk-secret-value" not in str(debug.values())
    assert isinstance(debug["mock_mode_parsed"], bool)
