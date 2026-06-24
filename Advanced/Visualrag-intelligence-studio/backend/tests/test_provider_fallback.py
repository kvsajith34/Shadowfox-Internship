"""Tests for the provider fallback / error-classification fix.

These tests directly target the reported bugs:
  - OpenAI RateLimitError and Gemini NotFound crashing instead of falling
    back cleanly.
  - A provider being permanently "pinned" to mock after a single failure
    (the root cause of "even after selecting Gemini/OpenAI/HF, the app
    behaves like mock mode").
  - rag_service.py checking the stale settings.MOCK_MODE instead of the
    actual runtime-resolved active provider (root cause of the "MOCK_MODE:
    using first 5/19 chunks, skipping ChromaDB" log appearing even when a
    real provider was selected).
"""
import pytest

import app.services.provider_router as pr
from app.core.config import settings as app_settings


# ─── Fake exception classes mirroring real SDK exception names ────────────────
# We don't need the REAL openai/google SDKs installed to test classification —
# _classify_provider_error() duck-types purely on type(exc).__name__, which is
# exactly what the user's own backend logs showed: "RateLimitError" / "NotFound".

class RateLimitError(Exception):
    """Stand-in for openai.RateLimitError — name matters, not implementation."""


class NotFound(Exception):
    """Stand-in for google.api_core.exceptions.NotFound — name matters."""


@pytest.fixture
def fake_sdk_available(monkeypatch):
    """Make check_sdk_available() return True so construction is actually
    attempted instead of short-circuiting on 'provider SDK error'."""
    monkeypatch.setattr(pr, "check_sdk_available", lambda provider: True)


@pytest.fixture(autouse=True)
def real_provider_runtime_mode():
    """These tests exercise the REAL-provider call path, which requires
    mock_mode=False in the runtime state (the same state Settings page saves
    to). conftest.py's session-wide MOCK_MODE=true env var only sets the
    .env-level default — the runtime/saved state (checked first by
    get_effective_mock_mode) must be explicitly set here, exactly like a
    user toggling Mock Mode off in Settings would. Restored after each test
    so this file's state never leaks into other test modules.
    """
    previous = dict(pr._runtime_state)
    pr._runtime_state["mock_mode"] = False
    pr._runtime_state["provider"] = None
    yield
    pr._runtime_state.clear()
    pr._runtime_state.update(previous)


@pytest.fixture(autouse=True)
def clear_fallback_cache():
    """Each test starts with a clean _last_fallback_reason/_last_provider_error_type
    cache so tests don't leak state into each other."""
    pr._last_fallback_reason.clear()
    pr._last_provider_error_type.clear()
    yield
    pr._last_fallback_reason.clear()
    pr._last_provider_error_type.clear()


# ─── 1. MOCK_MODE=false parses correctly (covered in test_settings.py too) ────

def test_mock_mode_false_parses_as_python_false():
    from app.core.config import Settings
    import os
    os.environ["MOCK_MODE"] = "false"
    try:
        assert Settings().MOCK_MODE is False
    finally:
        os.environ["MOCK_MODE"] = "true"


# ─── 2. Gemini key present is detected ─────────────────────────────────────────

def test_gemini_key_present_is_detected(monkeypatch):
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", "fake-gemini-key")
    from app.api.v1.settings_routes import _api_key_status
    assert _api_key_status()["gemini"] is True


# ─── 3. Gemini NotFound produces a fallback response, not a crash ─────────────

def test_gemini_notfound_falls_back_cleanly(monkeypatch, fake_sdk_available):
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", "fake-key")

    class FakeGeminiService:
        def visual_chat(self, **kwargs):
            raise NotFound("model not found")

    monkeypatch.setattr(pr, "_construct_service", lambda provider: FakeGeminiService())

    result, provider = pr.call_provider_method("visual_chat", provider_hint="gemini", message="hello")

    assert provider == "mock"
    assert result["response_provider"] == "mock"
    assert result["selected_provider"] == "gemini"
    assert result["provider_error_type"] == "NotFound"
    assert "gemini" in result["fallback_reason"].lower()
    assert "model" in result["fallback_reason"].lower()
    assert result["answer"]  # mock still produced a valid, non-empty answer


# ─── 4. OpenAI RateLimitError produces a fallback response, not a crash ────────

def test_openai_ratelimit_falls_back_cleanly(monkeypatch, fake_sdk_available):
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", "fake-key")

    class FakeOpenAIService:
        def visual_chat(self, **kwargs):
            raise RateLimitError("rate limited")

    monkeypatch.setattr(pr, "_construct_service", lambda provider: FakeOpenAIService())

    result, provider = pr.call_provider_method("visual_chat", provider_hint="openai", message="hello")

    assert provider == "mock"
    assert result["response_provider"] == "mock"
    assert result["selected_provider"] == "openai"
    assert result["provider_error_type"] == "RateLimitError"
    assert "rate limit" in result["fallback_reason"].lower()
    assert result["answer"]


def test_huggingface_failure_falls_back_cleanly(monkeypatch, fake_sdk_available):
    monkeypatch.setattr(app_settings, "HF_TOKEN", "fake-key")

    class FakeHFService:
        def visual_chat(self, **kwargs):
            raise RuntimeError("endpoint unavailable")

    monkeypatch.setattr(pr, "_construct_service", lambda provider: FakeHFService())

    result, provider = pr.call_provider_method("visual_chat", provider_hint="huggingface", message="hello")

    assert provider == "mock"
    assert "hugging face" in result["fallback_reason"].lower()
    assert result["answer"]


# ─── THE core regression test: one failure must NOT permanently pin to mock ───

def test_provider_failure_does_not_permanently_pin_to_mock(monkeypatch, fake_sdk_available):
    """Reproduces the exact reported symptom: 'Even after selecting Gemini,
    the app behaves like mock mode.' One failed call must fall back to mock
    for THAT request only — the very next call must try the real provider
    again, not stay silently pinned to mock forever."""
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", "fake-key")

    call_count = {"n": 0}

    class FlakyGeminiService:
        def visual_chat(self, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise NotFound("model not found")
            return {
                "answer": "real gemini answer", "evidence": [], "evaluation": {},
                "confidence_score": 0.9, "safety_notes": "", "hallucination_risk": "low",
                "suggested_followups": [],
            }

    monkeypatch.setattr(pr, "_construct_service", lambda provider: FlakyGeminiService())

    # First call fails -> falls back to mock for THIS request only.
    result1, provider1 = pr.call_provider_method("visual_chat", provider_hint="gemini", message="q1")
    assert provider1 == "mock"
    assert result1["provider_error_type"] == "NotFound"

    # Second call: the underlying issue is now resolved (service succeeds).
    # This must NOT still be pinned to mock — that was the actual bug.
    result2, provider2 = pr.call_provider_method("visual_chat", provider_hint="gemini", message="q2")
    assert provider2 == "gemini"
    assert result2["response_provider"] == "gemini"
    assert result2["answer"] == "real gemini answer"
    assert result2["fallback_reason"] is None
    assert result2["provider_error_type"] is None


def test_last_fallback_info_is_recorded_but_does_not_gate(monkeypatch, fake_sdk_available):
    """_last_fallback_reason/_last_provider_error_type are kept for
    /provider-debug display, but must never be consulted to block a fresh
    attempt at the real provider."""
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", "fake-key")

    class FakeOpenAIService:
        def visual_chat(self, **kwargs):
            raise RateLimitError("rate limited")

    monkeypatch.setattr(pr, "_construct_service", lambda provider: FakeOpenAIService())
    pr.call_provider_method("visual_chat", provider_hint="openai", message="q1")

    reason, error_type = pr.get_last_fallback_info("openai")
    assert error_type == "RateLimitError"
    assert "rate limit" in reason.lower()

    # Despite a recorded failure, get_provider_with_reason must still resolve
    # to "openai" (not short-circuit to mock) — the actual call will be
    # attempted again.
    provider, reason2 = pr.get_provider_with_reason("openai")
    assert provider == "openai"
    assert reason2 is None


# ─── 5. RAG passes full chunks to a real provider, not capped to 5 ─────────────

def test_rag_uses_real_provider_path_when_active_provider_not_mock(monkeypatch, fake_sdk_available):
    """rag_service must resolve the chunk strategy from the actual runtime
    provider state, not the stale settings.MOCK_MODE — this is the exact fix
    for the reported 'MOCK_MODE: using first 5/19 chunks, skipping ChromaDB'
    log appearing even when Gemini was selected."""
    monkeypatch.setattr(app_settings, "GOOGLE_API_KEY", "fake-key")

    from app.services.rag_service import rag_service
    from app.services.document_parser import document_parser

    nineteen_chunks = [{"text": f"Chunk {i} content about revenue."} for i in range(19)]
    monkeypatch.setattr(
        document_parser, "parse",
        lambda content, filename: {"text": "...", "metadata": {}, "chunks": nineteen_chunks, "page_count": 1},
    )

    captured = {}

    class FakeGeminiService:
        def rag_query(self, **kwargs):
            captured["chunks"] = kwargs.get("chunks")
            return {
                "answer": "ok", "sources": [], "retrieved_chunks": [],
                "faithfulness_score": 0.9, "relevance_score": 0.9,
                "direct_llm_comparison": "", "rag_grounded_answer": "ok",
                "hallucination_risk": "low",
            }

    monkeypatch.setattr(pr, "_construct_service", lambda provider: FakeGeminiService())

    result = rag_service.query(
        file_id="f1", question="What is the revenue?", use_rag=True,
        provider_hint="gemini", file_content=b"irrelevant raw bytes", filename="report.txt",
    )

    assert result["_effective_provider"] == "gemini"
    # Real-provider path: NOT capped to the mock fast-path's 5-chunk limit.
    assert captured["chunks"] is not None
    assert len(captured["chunks"]) == 19


def test_rag_mock_path_still_caps_to_five_chunks(monkeypatch):
    """The mock-mode fast path (no real provider active) should still cap to
    5 chunks for speed — this is a deliberate, separate behavior."""
    from app.services.rag_service import rag_service
    from app.services.document_parser import document_parser

    nineteen_chunks = [{"text": f"Chunk {i} content about revenue."} for i in range(19)]
    monkeypatch.setattr(
        document_parser, "parse",
        lambda content, filename: {"text": "...", "metadata": {}, "chunks": nineteen_chunks, "page_count": 1},
    )

    result = rag_service.query(
        file_id="f1", question="What is the revenue?", use_rag=True,
        provider_hint="mock", file_content=b"irrelevant raw bytes", filename="report.txt",
    )
    assert result["_effective_provider"] == "mock"
    assert len(result["retrieved_chunks"]) <= 5


# ─── 7. Different PDF questions return different mock responses ───────────────

def test_different_questions_same_chunks_produce_different_mock_answers():
    from app.services.mock_ai_service import MockAIService
    svc = MockAIService()
    same_chunks = ["Revenue for Q3 was $5.2M, up 14% year over year."]

    result_a = svc.rag_query(question="What was the revenue?", file_id="f1", chunks=same_chunks)
    result_b = svc.rag_query(question="What were the operating costs?", file_id="f1", chunks=same_chunks)

    assert result_a["answer"] != result_b["answer"]


# ─── 9. provider-debug returns no secrets, includes the new fields ────────────

def test_provider_debug_includes_last_fallback_fields_no_secrets(client, monkeypatch):
    secret = "sk-THIS-IS-A-SECRET-KEY-9999"
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", secret)

    r = client.get("/api/v1/provider-debug")
    assert r.status_code == 200
    assert secret not in r.text

    data = r.json()["data"]
    assert "last_fallback_reason" in data
    assert "last_provider_error_type" in data
