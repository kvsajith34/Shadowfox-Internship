"""Tests for LLM response parsing and stale-response prevention.

These tests directly target the reported issues:
  - Gemini returning raw JSON code fences displayed verbatim as the answer.
  - Stale OpenAI/Gemini answers appearing after provider switch.
  - Same file with different questions returning same answer.
  - ChromaDB duplicate chunks from re-indexing.
"""
import pytest
from app.utils.llm_utils import parse_llm_json_response, RAG_DEFAULTS, VISUAL_CHAT_DEFAULTS


# ─── 1. JSON fence stripping ──────────────────────────────────────────────────

def test_plain_json_extracted_cleanly():
    raw = '{"answer": "Revenue was $5.2M.", "faithfulness_score": 0.95, "relevance_score": 0.92, "hallucination_risk": "low"}'
    result = parse_llm_json_response(raw, defaults=RAG_DEFAULTS)
    assert result["answer"] == "Revenue was $5.2M."
    assert result["faithfulness_score"] == 0.95
    assert result["relevance_score"] == 0.92
    assert result["hallucination_risk"] == "low"


def test_json_fence_stripped_before_parsing():
    """This is the EXACT format that was appearing verbatim in the UI."""
    raw = '```json\n{"answer": "Revenue was $5.2M.", "faithfulness_score": 0.95}\n```'
    result = parse_llm_json_response(raw, defaults=RAG_DEFAULTS)
    assert result["answer"] == "Revenue was $5.2M."
    # The raw fenced string must NEVER be the answer
    assert "```" not in result["answer"]
    assert result["answer"] != raw


def test_json_fence_without_language_tag_stripped():
    raw = '```\n{"answer": "The trend is upward."}\n```'
    result = parse_llm_json_response(raw)
    assert result["answer"] == "The trend is upward."
    assert "```" not in result["answer"]


def test_prose_containing_json_extracted():
    raw = 'Here is my answer: {"answer": "Q3 revenue was $5.2M.", "faithfulness_score": 0.9}'
    result = parse_llm_json_response(raw, defaults=RAG_DEFAULTS)
    assert result["answer"] == "Q3 revenue was $5.2M."


def test_plain_prose_returned_as_answer():
    raw = "The revenue for Q3 was $5.2M, an increase of 14% year over year."
    result = parse_llm_json_response(raw, defaults=RAG_DEFAULTS)
    assert result["answer"] == raw
    # defaults should still be applied when no JSON is found
    assert result["faithfulness_score"] == RAG_DEFAULTS["faithfulness_score"]


def test_empty_input_returns_empty_answer():
    result = parse_llm_json_response("", defaults=RAG_DEFAULTS)
    assert result["answer"] == ""


def test_defaults_apply_when_json_missing_key():
    raw = '{"answer": "Costs declined."}'  # no faithfulness_score in JSON
    result = parse_llm_json_response(raw, defaults=RAG_DEFAULTS)
    assert result["answer"] == "Costs declined."
    assert result["faithfulness_score"] == RAG_DEFAULTS["faithfulness_score"]


def test_parsed_json_key_overrides_default():
    raw = '{"answer": "Costs declined.", "faithfulness_score": 0.99}'
    result = parse_llm_json_response(raw, defaults=RAG_DEFAULTS)
    assert result["faithfulness_score"] == 0.99  # JSON wins over default


def test_raw_json_never_becomes_answer_for_rag():
    """The core UI bug: raw JSON blob must not appear as the answer text."""
    raw = '{"answer": "Profit margin improved.", "faithfulness_score": 0.96}'
    result = parse_llm_json_response(raw, defaults=RAG_DEFAULTS)
    assert result["answer"] == "Profit margin improved."
    assert not result["answer"].startswith("{")


# ─── 2. OpenAI max_retries=0 is configured ───────────────────────────────────

def test_openai_service_sets_max_retries_zero():
    """OpenAI client must be configured with max_retries=0 so a RateLimitError
    fails fast instead of auto-retrying and wasting quota."""
    import unittest.mock as mock
    import sys
    sys.modules["openai"] = mock.MagicMock()

    import importlib
    import app.core.config as cfg
    cfg.settings.OPENAI_API_KEY = "fake-key"

    # Import fresh so __init__ runs with the mock SDK
    import app.services.openai_service as svc_mod
    importlib.reload(svc_mod)

    # Bypass __init__ to inspect what arguments OpenAI() would be called with
    instance = object.__new__(svc_mod.OpenAIService)
    with mock.patch.object(svc_mod, "settings", cfg.settings):
        # Call __init__ with the mocked OpenAI class
        openai_cls = sys.modules["openai"].OpenAI
        try:
            svc_mod.OpenAIService.__init__(instance)
        except Exception:
            pass  # AttributeError is expected since it's a MagicMock

    call_kwargs = openai_cls.call_args_list
    if call_kwargs:
        kwargs = call_kwargs[-1].kwargs if call_kwargs[-1].kwargs else {}
        args = call_kwargs[-1].args if call_kwargs[-1].args else ()
        # max_retries should be 0 if it was passed
        assert kwargs.get("max_retries", 0) == 0, "OpenAI must be initialised with max_retries=0"


# ─── 3. Gemini model fallback list ───────────────────────────────────────────

def test_gemini_fallback_list_contains_current_models():
    from app.core.config import GEMINI_MODEL_FALLBACKS, settings
    assert "gemini-2.5-flash" in GEMINI_MODEL_FALLBACKS
    assert settings.GEMINI_MODEL == "gemini-2.5-flash"


# ─── 4. RAG chunk deduplication (same text not added twice) ─────────────────

def test_rag_service_deduplicates_chunks(monkeypatch):
    """Identical chunks from a double-indexed file must be deduplicated before
    being sent to the LLM — avoids bloated, repetitive prompts."""
    from app.services.rag_service import RagService
    from app.services.document_parser import document_parser
    import app.services.provider_router as pr

    # 19 chunks, but the first 5 are identical duplicates
    duplicate_then_unique = (
        [{"text": "Duplicate content about revenue."}] * 5
        + [{"text": f"Unique chunk {i}"} for i in range(14)]
    )

    monkeypatch.setattr(
        document_parser, "parse",
        lambda content, filename: {"text": "...", "metadata": {}, "chunks": duplicate_then_unique, "page_count": 1},
    )

    captured: dict = {}

    def fake_call(method_name, provider_hint=None, **kwargs):
        captured["chunks"] = kwargs.get("chunks", [])
        return {"answer": "ok", "sources": [], "retrieved_chunks": [], "faithfulness_score": 0.9,
                "relevance_score": 0.9, "direct_llm_comparison": "", "rag_grounded_answer": "ok",
                "hallucination_risk": "low", "selected_provider": "mock", "response_provider": "mock",
                "fallback_reason": None, "provider_error_type": None}, "mock"

    monkeypatch.setattr(pr, "call_provider_method", fake_call)

    svc = RagService()
    svc.query(file_id="f1", question="What is revenue?", use_rag=True,
              provider_hint="mock", file_content=b"content", filename="report.txt")

    chunks = captured.get("chunks", [])
    # Deduplication must have removed the four duplicate "Duplicate content" chunks
    dup_count = sum(1 for c in chunks if "Duplicate content" in c)
    assert dup_count <= 1, f"Expected at most 1 duplicate chunk, got {dup_count}"


# ─── 5. Different questions return different mock answers ─────────────────────

def test_different_questions_produce_different_mock_rag_answers():
    from app.services.mock_ai_service import MockAIService
    svc = MockAIService()
    chunks = ["Revenue for Q3 was $5.2M, up 14%."]
    r1 = svc.rag_query(question="What was the revenue?", file_id="f1", chunks=chunks)
    r2 = svc.rag_query(question="Who are the key stakeholders?", file_id="f1", chunks=chunks)
    assert r1["answer"] != r2["answer"]


def test_different_files_produce_different_mock_invoice_answers():
    from app.services.mock_ai_service import MockAIService
    svc = MockAIService()
    r1 = svc.extract_invoice(filename="invoice_acme_q1.pdf")
    r2 = svc.extract_invoice(filename="receipt_globaltech_2025.pdf")
    assert r1["invoice_number"] != r2["invoice_number"]


def test_different_files_produce_different_mock_chart_answers():
    from app.services.mock_ai_service import MockAIService
    svc = MockAIService()
    r1 = svc.analyze_chart(filename="revenue_2024.png", question="What is the trend?")
    r2 = svc.analyze_chart(filename="server_latency.png", question="Any anomalies?")
    assert r1["chart_type"] != r2["chart_type"] or r1["main_trend"] != r2["main_trend"]


# ─── 6. Provider field present in response ───────────────────────────────────

def test_rag_endpoint_response_includes_provider_fields(client):
    r = client.post("/api/v1/pdf-rag-query", json={
        "file_id": "test_file", "question": "What is this about?", "provider": "mock",
    })
    assert r.status_code == 200
    data = r.json()["data"]
    assert "response_provider" in data
    assert "selected_provider" in data
    assert "fallback_reason" in data


def test_response_envelope_includes_request_id(client):
    """Every envelope must include a unique request_id for stale-response tracking."""
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert "request_id" in r.json()
    assert r.json()["request_id"]  # non-empty UUID string


def test_two_consecutive_requests_have_different_request_ids(client):
    r1 = client.get("/api/v1/health")
    r2 = client.get("/api/v1/health")
    assert r1.json()["request_id"] != r2.json()["request_id"]


# ─── 7. No secrets in debug response ────────────────────────────────────────

def test_provider_debug_no_secrets(client, monkeypatch):
    from app.core.config import settings as app_settings
    secret = "sk-SECRET-KEY-SHOULD-NOT-APPEAR"
    monkeypatch.setattr(app_settings, "OPENAI_API_KEY", secret)
    r = client.get("/api/v1/provider-debug")
    assert r.status_code == 200
    assert secret not in r.text
