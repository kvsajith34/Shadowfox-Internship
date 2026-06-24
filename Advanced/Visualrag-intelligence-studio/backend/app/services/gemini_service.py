"""Google Gemini service implementation."""
import json
from typing import Any, Dict, List, Optional
from app.core.config import settings, GEMINI_MODEL_FALLBACKS
from app.core.logging_config import get_logger
from app.utils.llm_utils import (
    parse_llm_json_response,
    RAG_DEFAULTS, CHART_DEFAULTS, VISUAL_CHAT_DEFAULTS, EVALUATE_DEFAULTS,
)

logger = get_logger(__name__)


def _file_context_line(filename: Optional[str], file_type: Optional[str], metadata: Optional[Dict[str, Any]]) -> str:
    """Build a short context line describing the file for the prompt, if any info is available."""
    if not (filename or file_type or metadata):
        return ""
    parts = []
    if filename:
        parts.append(f"filename: {filename}")
    if file_type:
        parts.append(f"type: {file_type}")
    if metadata:
        for k in ("page_count", "size_bytes"):
            if metadata.get(k):
                parts.append(f"{k}: {metadata[k]}")
    return f"\nFile context — {', '.join(parts)}." if parts else ""


class GeminiService:
    """Google Gemini API service for real AI-powered analysis.

    Note: full image-bytes vision support is not yet wired up — until then,
    this service answers from the question/text/metadata context it is
    given, rather than the raw image. This still produces useful, on-topic
    answers and never crashes when file metadata is passed in.

    Exceptions are NOT caught-and-converted-to-mock here. They propagate to
    the caller (provider_router.call_provider_method), which is the single
    place responsible for classifying the failure and falling back to mock
    for that request — this keeps the API response's provider field honest
    and avoids silently mislabeling a mock answer as "gemini".
    """

    PROVIDER = "gemini"

    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    def _generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate a response from Gemini.

        If the requested model raises NotFound (model name unavailable for
        this API version/region), retries across GEMINI_MODEL_FALLBACKS in
        order and logs which one succeeded. Any other exception type (auth,
        rate limit, network) fails fast without retrying — switching model
        names would not fix those, and retrying would waste quota.
        """
        import google.generativeai as genai

        primary = model or self.model_name
        candidates = [primary] + [m for m in GEMINI_MODEL_FALLBACKS if m != primary]

        last_exc: Optional[Exception] = None
        for candidate_model in candidates:
            try:
                active_model = (
                    self.model if candidate_model == self.model_name
                    else genai.GenerativeModel(candidate_model)
                )
                response = active_model.generate_content(prompt)
                if candidate_model != primary:
                    logger.info(
                        "Gemini fallback model succeeded: '%s' (primary '%s' was unavailable)",
                        candidate_model, primary,
                    )
                return response.text or ""
            except Exception as e:
                last_exc = e
                error_type = type(e).__name__
                logger.warning("Gemini model '%s' failed: %s", candidate_model, error_type)
                if error_type != "NotFound":
                    # Only NotFound (wrong/unavailable model name) is worth
                    # retrying with a different model. Auth/rate-limit/network
                    # errors won't be fixed by switching model names.
                    break

        logger.error("Gemini generation error: %s", type(last_exc).__name__ if last_exc else "Unknown")
        raise last_exc

    def visual_chat(
        self,
        message: str,
        file_id: Optional[str] = None,
        file_path: Optional[str] = None,
        filename: Optional[str] = None,
        file_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Visual chat using Gemini (text/metadata path until full vision support)."""
        ctx = _file_context_line(filename, file_type, metadata)
        prompt = (
            f"Analyze this visual content and answer: {message}{ctx}\n\n"
            "Return a JSON object with: answer, evidence (list), confidence_score (0-1), "
            "safety_notes, hallucination_risk (low/medium/high), suggested_followups (list)."
        )
        result = self._generate(prompt, model=model)
        parsed = parse_llm_json_response(result, defaults=VISUAL_CHAT_DEFAULTS)
        return {
            "answer": parsed.get("answer", result),
            "evidence": parsed.get("evidence", []),
            "evaluation": {"method": "gemini_vision", "model": model or self.model_name},
            "confidence_score": parsed.get("confidence_score", 0.8),
            "safety_notes": parsed.get("safety_notes", ""),
            "hallucination_risk": parsed.get("hallucination_risk", "low"),
            "suggested_followups": parsed.get("suggested_followups", []),
        }

    def rag_query(
        self,
        question: str,
        file_id: Optional[str] = None,
        chunks: Optional[List[str]] = None,
        file_path: Optional[str] = None,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_rag: bool = True,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """RAG query using Gemini — sends the question plus retrieved chunk
        context so the answer is grounded in the actual document content."""
        ctx = _file_context_line(filename, file_type=None, metadata=metadata)
        context = "\n\n".join(chunks) if chunks else "No specific document context provided."
        prompt = (
            f"Context:\n{context}{ctx}\n\nQuestion: {question}\n\n"
            "Answer based only on the context. Return JSON with: answer, "
            "faithfulness_score (0-1), relevance_score (0-1), hallucination_risk."
        )
        result = self._generate(prompt, model=model)
        parsed = parse_llm_json_response(result, defaults=RAG_DEFAULTS)
        return {
            "answer": parsed.get("answer", result),
            "sources": [{"chunk_id": f"chunk_{i}", "text": c[:200]} for i, c in enumerate(chunks or [])],
            "retrieved_chunks": [{"id": f"chunk_{i}", "text": c[:200], "similarity": 0.9 - i * 0.05} for i, c in enumerate(chunks[:5] if chunks else [])],
            "faithfulness_score": parsed.get("faithfulness_score", 0.85),
            "relevance_score": parsed.get("relevance_score", 0.88),
            "direct_llm_comparison": "RAG-grounded with Gemini analysis.",
            "rag_grounded_answer": parsed.get("answer", result),
            "hallucination_risk": parsed.get("hallucination_risk", "low"),
        }

    def extract_invoice(
        self,
        file_id: Optional[str] = None,
        file_path: Optional[str] = None,
        filename: Optional[str] = None,
        file_type: Optional[str] = None,
        extracted_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Extract invoice data using Gemini."""
        extracted_text = extracted_text or ""
        prompt = (
            f"Extract all invoice fields from this text:\n\n{extracted_text[:3000]}\n\n"
            "Return JSON with: vendor_name, customer_name, invoice_number, invoice_date, "
            "due_date, subtotal, tax_amount, total_amount, currency, payment_status, "
            "line_items, confidence_score."
        )
        result = self._generate(prompt, model=model)
        parsed = parse_llm_json_response(result)
        return {
            "vendor_name": parsed.get("vendor_name", ""),
            "customer_name": parsed.get("customer_name", ""),
            "invoice_number": parsed.get("invoice_number", ""),
            "invoice_date": parsed.get("invoice_date", ""),
            "due_date": parsed.get("due_date", ""),
            "subtotal": parsed.get("subtotal", 0),
            "tax_amount": parsed.get("tax_amount", 0),
            "total_amount": parsed.get("total_amount", 0),
            "currency": parsed.get("currency", "USD"),
            "payment_status": parsed.get("payment_status", "unknown"),
            "line_items": parsed.get("line_items", []),
            "missing_fields": [],
            "confidence_score": parsed.get("confidence_score", 0.85),
            "safety_note": "Extracted via Gemini. Recommend verification.",
            "raw_extracted_text": extracted_text[:500],
        }

    def analyze_chart(
        self,
        question: Optional[str] = None,
        file_id: Optional[str] = None,
        file_path: Optional[str] = None,
        filename: Optional[str] = None,
        file_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        extracted_text: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Analyze chart using Gemini."""
        question = question or ""
        extracted_text = extracted_text or ""
        ctx = _file_context_line(filename, file_type, metadata)
        prompt = (
            f"Analyze this chart data:\n\n{extracted_text[:2000]}{ctx}\n\n"
            f"{f'Question: {question}' if question else ''}\n\n"
            "Return JSON: chart_type, title, main_trend, highest_value, lowest_value, "
            "key_insights, confidence_score, answer."
        )
        result = self._generate(prompt, model=model)
        parsed = parse_llm_json_response(result, defaults=CHART_DEFAULTS)
        return {
            "chart_type": parsed.get("chart_type", "unknown"),
            "title": parsed.get("title", ""),
            "main_trend": parsed.get("main_trend", ""),
            "highest_value": parsed.get("highest_value", ""),
            "lowest_value": parsed.get("lowest_value", ""),
            "key_insights": parsed.get("key_insights", []),
            "possible_limitations": parsed.get("possible_limitations", []),
            "data_table": parsed.get("data_table", []),
            "confidence_score": parsed.get("confidence_score", 0.8),
            "answer": parsed.get("answer", result),
            "evaluation": {"method": "gemini_chart", "model": model or self.model_name},
        }

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        evidence: Optional[List[str]] = None,
        task_type: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Evaluate an answer using Gemini."""
        evidence = evidence or []
        task_type = task_type or "visual_chat"
        prompt = (
            f"Evaluate this answer:\nQuestion: {question}\nAnswer: {answer}\n"
            f"Evidence: {json.dumps(evidence[:5])}\n\n"
            "Return JSON: relevance_score, faithfulness_score, completeness_score, "
            "safety_score, hallucination_risk, improvement_suggestions."
        )
        result = self._generate(prompt, model=model)
        parsed = parse_llm_json_response(result, defaults=EVALUATE_DEFAULTS)
        return {
            "relevance_score": parsed.get("relevance_score", 0.8),
            "faithfulness_score": parsed.get("faithfulness_score", 0.8),
            "completeness_score": parsed.get("completeness_score", 0.8),
            "safety_score": parsed.get("safety_score", 0.9),
            "hallucination_risk": parsed.get("hallucination_risk", "low"),
            "missing_evidence": parsed.get("missing_evidence", []),
            "risk_explanation": parsed.get("risk_explanation", ""),
            "improvement_suggestions": parsed.get("improvement_suggestions", []),
        }
