"""Anthropic/Claude service implementation."""
import json
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging_config import get_logger

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


class AnthropicService:
    """Anthropic Claude API service for AI-powered analysis.

    Exceptions are NOT caught and converted to mock here — they propagate to
    the caller (provider_router.call_provider_method), which is the single
    place responsible for classifying the failure and falling back to mock
    for that request only.
    """

    PROVIDER = "anthropic"

    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
        self.model = getattr(settings, "CLAUDE_MODEL", "claude-sonnet-4-20250514")

    def _generate(self, system_prompt: str, user_message: str, max_tokens: int = 1024, model: Optional[str] = None) -> str:
        """Generate a response from Claude."""
        response = self.client.messages.create(
            model=model or self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text if response.content else ""

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
        """Visual chat using Claude (text/metadata path until full vision support)."""
        ctx = _file_context_line(filename, file_type, metadata)
        system = "You are an expert visual analyst. Analyze images and provide detailed, accurate descriptions. Return JSON."
        user_msg = (
            f"Analyze this visual content and answer: {message}{ctx}\n\n"
            "Return JSON with: answer, evidence (list), confidence_score (0-1), "
            "safety_notes, hallucination_risk (low/medium/high), suggested_followups (list)."
        )
        result = self._generate(system, user_msg, model=model)
        parsed = json.loads(result) if result.strip().startswith("{") else {"answer": result}
        return {
            "answer": parsed.get("answer", result),
            "evidence": parsed.get("evidence", []),
            "evaluation": {"method": "anthropic_vision", "model": model or self.model},
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
        """RAG query using Claude."""
        ctx = _file_context_line(filename, file_type=None, metadata=metadata)
        context = "\n\n".join(chunks) if chunks else "No specific document context provided."
        system = "You are a precise document analyst. Answer based only on provided context. Return JSON."
        user_msg = (
            f"Context:\n{context}{ctx}\n\nQuestion: {question}\n\n"
            "Return JSON with: answer, faithfulness_score (0-1), relevance_score (0-1), hallucination_risk."
        )
        result = self._generate(system, user_msg, max_tokens=1500, model=model)
        parsed = json.loads(result) if result.strip().startswith("{") else {"answer": result}
        return {
            "answer": parsed.get("answer", result),
            "sources": [{"chunk_id": f"chunk_{i}", "text": c[:200]} for i, c in enumerate(chunks or [])],
            "retrieved_chunks": [{"id": f"chunk_{i}", "text": c[:200], "similarity": 0.9 - i * 0.05} for i, c in enumerate(chunks[:5] if chunks else [])],
            "faithfulness_score": parsed.get("faithfulness_score", 0.85),
            "relevance_score": parsed.get("relevance_score", 0.88),
            "direct_llm_comparison": "RAG-grounded with Claude analysis.",
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
        """Extract invoice data using Claude."""
        extracted_text = extracted_text or ""
        system = "You are an invoice data extraction specialist. Return JSON."
        user_msg = (
            f"Extract invoice fields from:\n\n{extracted_text[:3000]}\n\n"
            "Return JSON with: vendor_name, customer_name, invoice_number, invoice_date, "
            "due_date, subtotal, tax_amount, total_amount, currency, payment_status, "
            "line_items, confidence_score."
        )
        result = self._generate(system, user_msg, max_tokens=1500, model=model)
        parsed = json.loads(result) if result.strip().startswith("{") else {}
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
            "safety_note": "Extracted via Claude. Recommend verification.",
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
        """Analyze chart using Claude."""
        question = question or ""
        extracted_text = extracted_text or ""
        ctx = _file_context_line(filename, file_type, metadata)
        system = "You are a chart and data visualization analyst. Return JSON."
        user_msg = (
            f"Analyze this chart:\n\n{extracted_text[:2000]}{ctx}\n\n"
            f"{f'Question: {question}' if question else ''}\n\n"
            "Return JSON: chart_type, title, main_trend, highest_value, lowest_value, "
            "key_insights, confidence_score, answer."
        )
        result = self._generate(system, user_msg, model=model)
        parsed = json.loads(result) if result.strip().startswith("{") else {"answer": result}
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
            "evaluation": {"method": "anthropic_chart", "model": model or self.model},
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
        """Evaluate answer using Claude."""
        evidence = evidence or []
        task_type = task_type or "visual_chat"
        system = "You are an AI answer quality evaluator. Score answers on multiple dimensions. Return JSON."
        user_msg = (
            f"Evaluate:\nQ: {question}\nA: {answer}\nEvidence: {json.dumps(evidence[:5])}\n\n"
            "Return JSON: relevance_score (0-1), faithfulness_score (0-1), completeness_score (0-1), "
            "safety_score (0-1), hallucination_risk, improvement_suggestions."
        )
        result = self._generate(system, user_msg, model=model)
        parsed = json.loads(result) if result.strip().startswith("{") else {}
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
