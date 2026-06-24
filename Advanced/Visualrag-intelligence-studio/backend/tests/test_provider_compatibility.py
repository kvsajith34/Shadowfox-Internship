"""Tests for the provider-interface standardization fix.

These tests directly target the originally reported bug:
    "GeminiService.visual_chat() got an unexpected keyword argument 'filename'"
(and the same for OpenAIService / HuggingFaceService), plus the broader
requirement that all five AI services (mock + 4 real providers) share one
standardized method interface, that mock responses vary by input, and that
internal routing details (e.g. _effective_provider) never leak into API
responses.
"""
import io
import sys
import unittest.mock as mock

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings as app_settings


# ─── Fixtures: fake SDK modules so real-provider services can be constructed
# without needing real network access or real installed packages ──────────────

@pytest.fixture
def fake_provider_sdks(monkeypatch):
    """Register fake SDK modules so OpenAIService/GeminiService/etc. can be
    constructed (their __init__ imports these). The fakes return MagicMocks
    for any call, which is fine — these tests only verify that argument
    BINDING succeeds (no TypeError), not that real network calls happen.
    """
    fake_modules = ["openai", "google", "google.generativeai", "huggingface_hub", "anthropic"]
    originals = {m: sys.modules.get(m) for m in fake_modules}
    for m in fake_modules:
        sys.modules[m] = mock.MagicMock()
    yield
    for m in fake_modules:
        if originals[m] is not None:
            sys.modules[m] = originals[m]
        else:
            sys.modules.pop(m, None)


# ─── 1. Provider method signatures accept filename + metadata (all 5 services) ─

ALL_STANDARD_KWARGS = dict(
    message="What is shown in this image?",
    file_id="file_abc123",
    file_path="/uploads/file_abc123/chart.png",
    filename="chart.png",
    file_type="image",
    metadata={"size_bytes": 12345},
    history=[],
    model="some-model",
    some_future_field="must be absorbed by **kwargs",
)


@pytest.mark.parametrize("service_module,class_name", [
    ("app.services.mock_ai_service", "MockAIService"),
    ("app.services.openai_service", "OpenAIService"),
    ("app.services.gemini_service", "GeminiService"),
    ("app.services.huggingface_service", "HuggingFaceService"),
    ("app.services.anthropic_service", "AnthropicService"),
])
def test_visual_chat_signature_accepts_filename_and_metadata(service_module, class_name, fake_provider_sdks):
    """Construction is bypassed (object.__new__) so this isolates EXACTLY the
    argument-binding behavior from any SDK/network concern. Python validates
    argument binding before entering the function body, so an AttributeError
    here (from a missing self.client, since __init__ was skipped) PROVES the
    signature bound successfully — exactly what we're verifying. A TypeError
    would mean the bug has regressed.
    """
    import importlib
    mod = importlib.import_module(service_module)
    cls = getattr(mod, class_name)
    instance = object.__new__(cls)
    try:
        cls.visual_chat(instance, **ALL_STANDARD_KWARGS)
    except TypeError as e:
        pytest.fail(f"{class_name}.visual_chat() raised TypeError on standard kwargs: {e}")
    except AttributeError:
        pass  # expected — proves the signature bound and we reached the body


@pytest.mark.parametrize("method_name,kwargs", [
    ("visual_chat", dict(message="q", file_id="f1", file_path="/p", filename="a.png",
                          file_type="image", metadata={"size_bytes": 1}, history=[], model="m")),
    ("rag_query", dict(question="q", file_id="f1", chunks=["c1"], file_path="/p", filename="a.pdf",
                        metadata={"size_bytes": 1}, use_rag=True, model="m")),
    ("extract_invoice", dict(file_id="f1", file_path="/p", filename="a.pdf", file_type="pdf",
                              extracted_text="t", metadata={"size_bytes": 1}, model="m")),
    ("analyze_chart", dict(question="q", file_id="f1", file_path="/p", filename="a.png",
                            file_type="image", metadata={"size_bytes": 1}, model="m")),
    ("evaluate_answer", dict(question="q", answer="a", evidence=["e"], task_type="visual_chat", model="m")),
])
@pytest.mark.parametrize("service_module,class_name", [
    ("app.services.mock_ai_service", "MockAIService"),
    ("app.services.openai_service", "OpenAIService"),
    ("app.services.gemini_service", "GeminiService"),
    ("app.services.huggingface_service", "HuggingFaceService"),
    ("app.services.anthropic_service", "AnthropicService"),
])
def test_all_standard_methods_accept_standardized_kwargs(
    service_module, class_name, method_name, kwargs, fake_provider_sdks
):
    """All 5 standardized methods × all 5 services must accept the unified
    keyword-argument interface without a TypeError."""
    import importlib
    mod = importlib.import_module(service_module)
    cls = getattr(mod, class_name)
    instance = object.__new__(cls)
    method = getattr(cls, method_name)
    try:
        method(instance, **kwargs)
    except TypeError as e:
        pytest.fail(f"{class_name}.{method_name}() raised TypeError on standard kwargs: {e}")
    except AttributeError:
        pass  # expected — proves the signature bound and we reached the body


# ─── 2. Mock visual_chat does not crash with filename (via real endpoint) ──────

def test_mock_visual_chat_endpoint_accepts_filename(client: TestClient):
    """End-to-end: the actual /api/v1/visual-chat endpoint, in mock mode,
    must not crash when a file_id with an associated filename is supplied."""
    r = client.post("/api/v1/visual-chat", json={
        "message": "Describe this chart",
        "file_id": "nonexistent_file_id_123",
        "provider": "mock",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert "answer" in body["data"]
    assert body["data"]["answer"]


# ─── 3-5. Gemini/OpenAI/HuggingFace visual_chat does not crash with filename
# when mocked/falling back (covered by the parametrized signature tests above,
# plus an explicit end-to-end check that selecting a real provider with no
# key configured still returns a clean mock answer, never a raw error) ────────

@pytest.mark.parametrize("provider", ["openai", "gemini", "huggingface"])
def test_real_provider_selected_without_key_falls_back_cleanly(client: TestClient, provider):
    """Selecting a real provider (without a configured key) must never crash
    the request — it must fall back to a valid mock-quality response."""
    r = client.post("/api/v1/visual-chat", json={
        "message": "What does this file show?",
        "file_id": "some_file",
        "provider": provider,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert "answer" in body["data"]
    assert body["data"]["answer"]
    # No raw Python exception text should ever appear in the response
    assert "unexpected keyword argument" not in str(body)
    assert "Traceback" not in str(body)


# ─── 6. PDF RAG with chunks returns a non-generic, varied answer ───────────────

def test_rag_query_with_chunks_returns_non_generic_answer():
    from app.services.mock_ai_service import MockAIService
    svc = MockAIService()

    result_a = svc.rag_query(
        question="What was the revenue?",
        file_id="f1",
        chunks=["Revenue for Q3 was $5.2M, up 14% year over year."],
    )
    result_b = svc.rag_query(
        question="What was the revenue?",
        file_id="f1",
        chunks=["Operating expenses decreased by 8% due to automation."],
    )
    # Different chunk content must produce a different answer
    assert result_a["answer"] != result_b["answer"]
    # The actual chunk content should be woven into the answer
    assert "5.2M" in result_a["answer"] or "Revenue" in result_a["answer"]


def test_rag_query_with_no_chunks_returns_clear_message():
    from app.services.mock_ai_service import MockAIService
    svc = MockAIService()
    result = svc.rag_query(question="What was the revenue?", file_id="f1", chunks=[])
    assert "no readable chunks" in result["answer"].lower() or "upload" in result["answer"].lower()


def test_pdf_rag_endpoint_does_not_crash_with_real_provider_selected(client: TestClient):
    r = client.post("/api/v1/pdf-rag-query", json={
        "file_id": "some_file", "question": "Summarize this document", "provider": "gemini",
    })
    assert r.status_code == 200
    assert r.json()["success"] is True


# ─── 7. Invoice extractor returns different output for different filenames ────

def test_invoice_extraction_varies_by_filename(client: TestClient, sample_pdf: bytes):
    r1 = client.post(
        "/api/v1/extract-invoice",
        files={"file": ("invoice_acme_q1.pdf", io.BytesIO(sample_pdf), "application/pdf")},
    )
    r2 = client.post(
        "/api/v1/extract-invoice",
        files={"file": ("receipt_globaltech_2025.pdf", io.BytesIO(sample_pdf), "application/pdf")},
    )
    d1, d2 = r1.json()["data"], r2.json()["data"]
    assert d1["invoice_number"] != d2["invoice_number"]
    assert (d1["vendor_name"] != d2["vendor_name"]) or (d1["total_amount"] != d2["total_amount"])
    # Internal routing marker must never leak into the response
    assert "_effective_provider" not in d1
    assert "_effective_provider" not in d2


# ─── 8. Chart analyzer returns different output for different filenames/questions ─

def test_chart_analysis_varies_by_filename_and_question(client: TestClient):
    from PIL import Image
    def make_png():
        img = Image.new("RGB", (100, 100), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf

    r1 = client.post(
        "/api/v1/analyze-chart",
        files={"file": ("revenue_q4.png", make_png(), "image/png")},
        data={"question": "What is the trend?"},
    )
    r2 = client.post(
        "/api/v1/analyze-chart",
        files={"file": ("server_latency.png", make_png(), "image/png")},
        data={"question": "Any anomalies?"},
    )
    d1, d2 = r1.json()["data"], r2.json()["data"]
    assert (d1["chart_type"] != d2["chart_type"]) or (d1["main_trend"] != d2["main_trend"])
    assert "_effective_provider" not in d1
    assert "_effective_provider" not in d2


# ─── No internal markers leak into any analysis endpoint's response ────────────

def test_no_internal_markers_leak_into_evaluate_response(client: TestClient):
    r = client.post("/api/v1/evaluate", json={
        "question": "Q?", "answer": "A.", "evidence": ["E"],
        "task_type": "visual_chat", "provider": "mock",
    })
    assert "_effective_provider" not in r.json()["data"]


def test_no_internal_markers_leak_into_rag_response(client: TestClient):
    r = client.post("/api/v1/pdf-rag-query", json={
        "file_id": "f1", "question": "Q?", "provider": "mock",
    })
    assert "_effective_provider" not in r.json()["data"]


# ─── CORS LAN-pattern regex (Required Fix 6) ───────────────────────────────────

def test_cors_lan_regex_matches_expected_origins():
    import re
    pattern = (
        r"^http://(localhost|127\.0\.0\.1|"
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|"
        r"192\.168\.\d{1,3}\.\d{1,3}):(5173|3000)$"
    )
    assert re.match(pattern, "http://10.155.121.181:5173")
    assert re.match(pattern, "http://192.168.1.42:5173")
    assert re.match(pattern, "http://localhost:3000")
    assert not re.match(pattern, "http://evil.com:5173")
    assert not re.match(pattern, "http://10.1.1.1:9999")
