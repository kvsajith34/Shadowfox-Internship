"""LLM response parsing utilities.

LLMs (Gemini, OpenAI, etc.) instructed to "return JSON" often wrap their
response in markdown code fences (```json ... ```) or add surrounding prose.
Feeding raw fenced JSON back to the frontend as the `answer` field is the
direct cause of the "ugly JSON displayed instead of clean answer" bug.

This module provides a single, shared parse helper used by every provider
service so the stripping and extraction logic lives in one place.
"""
import json
import re
from typing import Any, Dict, Optional


def parse_llm_json_response(
    raw: str,
    defaults: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Parse a JSON response from an LLM, handling all common formats.

    Handles:
      1. Plain JSON object:         { "answer": "..." }
      2. ```json fence:             ```json\n{ ... }\n```
      3. ``` fence (no language):   ```\n{ ... }\n```
      4. JSON embedded in prose:    "Here is your answer: { ... }"
      5. Total failure:             treat entire raw text as the answer

    Parameters
    ----------
    raw:      The raw string returned by the LLM.
    defaults: Dict of default values applied BEFORE parsed keys — so a parsed
              key always wins over a default, but missing keys get sensible
              values (e.g. fallback faithfulness_score).

    Returns a dict that always includes at least `{"answer": <something>}`.
    The returned answer is NEVER a raw code-fenced JSON blob.
    """
    defaults = defaults or {}
    text = raw.strip() if raw else ""

    if not text:
        return {**defaults, "answer": ""}

    # ── Step 1: strip markdown code fences ──────────────────────────────────
    # Matches ```json ... ``` and ``` ... ``` (with optional newlines inside)
    fence_pattern = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)
    fence_match = fence_pattern.search(text)
    if fence_match:
        text = fence_match.group(1).strip()

    # ── Step 2: try to parse the (now possibly de-fenced) text as JSON ──────
    parsed = _try_json_parse(text)
    if parsed is not None:
        merged = {**defaults, **parsed}
        # Guarantee "answer" key exists even if the LLM omitted it
        if "answer" not in merged or not merged["answer"]:
            merged["answer"] = raw  # last resort: raw text
        return merged

    # ── Step 3: try to find a JSON object embedded anywhere in the text ─────
    json_obj_pattern = re.compile(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}", re.DOTALL)
    for match in json_obj_pattern.finditer(text):
        parsed = _try_json_parse(match.group())
        if parsed is not None:
            merged = {**defaults, **parsed}
            if "answer" not in merged or not merged["answer"]:
                merged["answer"] = raw
            return merged

    # ── Step 4: treat the entire text as the answer (no JSON found) ─────────
    return {**defaults, "answer": text or raw}


def _try_json_parse(text: str) -> Optional[Dict[str, Any]]:
    """Attempt JSON parsing; return None (never raise) on failure."""
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    return None


# ─── Convenience extraction helpers ──────────────────────────────────────────

RAG_DEFAULTS: Dict[str, Any] = {
    "answer": "",
    "faithfulness_score": 0.85,
    "relevance_score": 0.88,
    "hallucination_risk": "low",
}

CHART_DEFAULTS: Dict[str, Any] = {
    "answer": "",
    "chart_type": "unknown",
    "title": "",
    "main_trend": "",
    "highest_value": "",
    "lowest_value": "",
    "key_insights": [],
    "possible_limitations": [],
    "data_table": [],
    "confidence_score": 0.80,
}

VISUAL_CHAT_DEFAULTS: Dict[str, Any] = {
    "answer": "",
    "evidence": [],
    "confidence_score": 0.80,
    "safety_notes": "",
    "hallucination_risk": "low",
    "suggested_followups": [],
}

EVALUATE_DEFAULTS: Dict[str, Any] = {
    "relevance_score": 0.80,
    "faithfulness_score": 0.80,
    "completeness_score": 0.80,
    "safety_score": 0.90,
    "hallucination_risk": "low",
    "missing_evidence": [],
    "risk_explanation": "",
    "improvement_suggestions": [],
}
