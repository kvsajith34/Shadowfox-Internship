"""Mock AI service — deterministic, file-aware, question-aware responses.

Design principles:
  - All variability is seeded from input data (filename + question + file_id +
    file size) so the *same* input always returns the *same* output.
  - Different inputs produce visibly different outputs.
  - Every method uses actual passed-in content (chunks, text, question) where
    available so responses feel contextually correct.
  - No random() calls without a deterministic seed.
  - Every method accepts the FULL standardized provider signature (file_id,
    file_path, filename, file_type, metadata, model, **kwargs) so it is a
    drop-in, never-crashes fallback for any real provider service.
"""
import hashlib
import os
from typing import Any, Dict, List, Optional


# ─── Deterministic helpers ────────────────────────────────────────────────────

def _rng(*parts: Any):
    """Return a seeded random.Random instance from the given parts."""
    import random
    key = "|".join(str(s).lower().strip() for s in parts if s)
    digest = hashlib.md5(key.encode()).hexdigest()
    return random.Random(int(digest[:8], 16))


def _stem(filename: Optional[str]) -> str:
    """Filename → human-readable title (no extension, spaced, title-cased)."""
    base = os.path.splitext(os.path.basename(filename or "document"))[0]
    return base.replace("_", " ").replace("-", " ").title()


def _size_hint(metadata: Optional[Dict[str, Any]]) -> str:
    """Extract a size value from metadata for fingerprinting, if present."""
    if not metadata:
        return ""
    for key in ("size_bytes", "size", "file_size", "bytes"):
        if key in metadata and metadata[key]:
            return str(metadata[key])
    return ""


def _intent(message: str) -> str:
    """Classify the rough intent of a question."""
    m = (message or "").lower()
    if any(w in m for w in ["summarize", "summary", "overview", "brief", "tldr"]):
        return "summarize"
    if any(w in m for w in ["extract", "find text", "read text", "ocr", "transcribe"]):
        return "extract"
    if any(w in m for w in ["compare", "difference", "versus", " vs ", "contrast"]):
        return "compare"
    if any(w in m for w in ["explain", "how does", "why ", "reason", "cause"]):
        return "explain"
    if any(w in m for w in ["analyze", "analysis", "interpret", "breakdown", "break down"]):
        return "analyze"
    if any(w in m for w in ["bottleneck", "issue", "problem", "error", "fix", "optimize"]):
        return "diagnose"
    if any(w in m for w in ["chart", "graph", "trend", "metric", "number", "value", "data"]):
        return "chart"
    return "describe"


# ─── MockAIService ────────────────────────────────────────────────────────────

class MockAIService:
    """Realistic mock AI responses that vary deterministically by input.

    Every method's signature matches the standardized provider interface
    (see provider_router.py docstring) and accepts **kwargs so any future
    metadata field never causes a crash here — this is the guaranteed-safe
    fallback every real provider service degrades to on failure.
    """

    PROVIDER = "mock"

    # ── Visual Chat ───────────────────────────────────────────────────────────

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
        rng = _rng(file_id or "", message, filename or "", _size_hint(metadata))
        title = _stem(filename) if filename else (f"file {(file_id or 'unknown')[:8]}")
        intent = _intent(message)
        ftype = (file_type or "").lower()

        doc_desc = {
            "pdf":   "PDF document",
            "image": "image file",
            "text":  "text document",
            "csv":   "data spreadsheet",
        }.get(ftype, "uploaded file")

        intros = [
            f"Mock visual analysis based on filename and metadata for **{title}** ({doc_desc}): ",
            f"Analyzing **{title}** ({doc_desc}) — mock visual analysis based on filename and metadata: ",
            f"Based on the filename and metadata of **{title}**: ",
            f"From **{title}** (mock visual analysis based on filename and metadata): ",
        ]
        intro = rng.choice(intros)

        bodies = {
            "summarize": [
                f"This {doc_desc} covers {rng.choice(['three','four','five','six'])} main topics. "
                f"The structure follows a {rng.choice(['logical','hierarchical','sequential','thematic'])} "
                f"arrangement with {rng.choice(['clear headings','labeled sections','color-coded regions','annotated areas'])}. "
                f"Key themes: {rng.choice(['system architecture','data pipeline','business metrics','technical specifications'])} "
                f"and {rng.choice(['performance analysis','risk assessment','operational workflow','cost breakdown'])}.",
                f"The {doc_desc} presents a {rng.choice(['comprehensive','concise','detailed','structured'])} summary "
                f"across {rng.choice(['2','3','5','7'])} sections. Notable elements include "
                f"{rng.choice(['charts','tables','diagrams','code blocks'])} illustrating "
                f"{rng.choice(['quarterly results','system topology','data flows','user journeys'])}.",
            ],
            "extract": [
                f"I detected the following text elements in **{title}**: headings at the top, "
                f"{rng.choice(['numbered lists','bullet points','tables','paragraphs'])} in the body, "
                f"and {rng.choice(['footer notes','captions','labels','annotations'])} throughout. "
                f"The text is {rng.choice(['left-aligned','centered','in two columns','single-column'])} "
                f"with approximately {rng.randint(150,800)} visible words.",
                f"Text extraction from **{title}** found {rng.randint(3,12)} distinct text regions. "
                f"Primary content includes {rng.choice(['headings and subheadings','data labels','table entries','paragraph text'])}. "
                f"Font styles detected: {rng.choice(['sans-serif','mixed serif/sans','monospace sections','bold headings'])}.",
            ],
            "describe": [
                f"The {doc_desc} **{title}** features a {rng.choice(['clean','complex','minimal','detailed'])} layout "
                f"with {rng.choice(['blue and white','dark and light','multi-color','monochromatic'])} color scheme. "
                f"Content is organized into {rng.randint(2,6)} visual zones. "
                f"The design suggests a {rng.choice(['technical report','business presentation','academic paper','operational dashboard'])}.",
                f"**{title}** is a {rng.choice(['structured','data-rich','visually organized','well-formatted'])} {doc_desc}. "
                f"I can identify {rng.randint(2,5)} main content areas containing "
                f"{rng.choice(['text and graphics','data tables','flowcharts','annotated diagrams'])}.",
            ],
            "analyze": [
                f"Analysis of **{title}** reveals {rng.randint(2,5)} key patterns: "
                f"({rng.randint(1,3)}) {rng.choice(['high information density in the upper section','dominant visual hierarchy from left to right','clear separation of data layers','color encoding for categorical data'])}, "
                f"({rng.randint(2,4)}) {rng.choice(['cross-references between sections','data validation indicators','trend annotations','comparative baseline markers'])}, "
                f"({rng.randint(3,5)}) {rng.choice(['summary statistics in the footer','legend-driven navigation','time-series progression','hierarchical decomposition'])}.",
            ],
            "diagnose": [
                f"Examining **{title}** for issues: "
                f"I identified {rng.randint(1,4)} potential {rng.choice(['bottlenecks','inefficiencies','data gaps','inconsistencies'])}. "
                f"Primary concern is {rng.choice(['the overloaded processing layer','missing validation steps','high latency in the secondary path','unbalanced load distribution'])}. "
                f"Recommendation: {rng.choice(['redistribute workload','add caching layer','implement retry logic','scale horizontally'])}.",
            ],
            "compare": [
                f"Comparing elements in **{title}**: "
                f"The {rng.choice(['left','upper','primary','first'])} section shows "
                f"{rng.choice(['higher throughput','better coverage','lower latency','greater capacity'])} "
                f"while the {rng.choice(['right','lower','secondary','second'])} section demonstrates "
                f"{rng.choice(['more stability','higher precision','lower error rate','better consistency'])}. "
                f"Overall {rng.choice(['the difference is significant','results are comparable','tradeoffs are clear','performance gap is notable'])}.",
            ],
            "explain": [
                f"**{title}** explains the {rng.choice(['end-to-end flow','core mechanism','architectural decision','operational process'])} as follows: "
                f"The {rng.choice(['input stage','initial layer','first component','entry point'])} receives "
                f"{rng.choice(['raw data','user requests','file uploads','API calls'])}, processes them through "
                f"{rng.choice(['a transformation pipeline','a validation layer','a routing mechanism','an enrichment step'])}, "
                f"and delivers {rng.choice(['structured output','transformed results','validated responses','enriched data'])}.",
            ],
            "chart": [
                f"The data visualization in **{title}** shows a "
                f"{rng.choice(['bar','line','area','scatter'])} chart with "
                f"{rng.choice(['upward','downward','stable','cyclical'])} trend. "
                f"Peak value appears at {rng.choice(['Q4','month 6','week 12','the final period'])} "
                f"({rng.choice(['$2.4M','94%','1,250 units','87 req/s'])}). "
                f"The data suggests {rng.choice(['seasonal patterns','consistent growth','performance plateau','accelerating adoption'])}.",
            ],
        }

        body_options = bodies.get(intent, bodies["describe"])
        body = rng.choice(body_options)
        answer = intro + body

        if message and len(message) < 120:
            answer += f'\n\nRegarding "{message}": ' + rng.choice([
                f"The {doc_desc} provides direct evidence supporting this inquiry.",
                f"Based on the visual content, the answer appears in the {rng.choice(['upper','middle','lower'])} section.",
                f"This is addressed in the {rng.choice(['first','second','third'])} content block of the document.",
            ])

        confidence = round(rng.uniform(0.76, 0.96), 2)
        risk = "low" if confidence > 0.84 else "medium"

        return {
            "answer": answer,
            "evidence": [
                f"Mock visual analysis of '{filename or file_id or 'uploaded file'}' (task: {intent})",
                f"Content type detected: {doc_desc}",
                f"Analysis method: deterministic mock — seed from filename+question",
            ],
            "evaluation": {"method": "mock_visual_analysis", "intent": intent, "quality": "demo"},
            "confidence_score": confidence,
            "safety_notes": "Content appears safe. Mock mode — no real vision model used.",
            "hallucination_risk": risk,
            "suggested_followups": rng.sample([
                "Can you extract all text visible in this document?",
                "What are the main data points or metrics shown?",
                "Describe the layout and visual hierarchy.",
                "Are there any charts or graphs in this image?",
                "What is the primary purpose of this document?",
                "Identify any tables or structured data.",
            ], k=3),
        }

    # ── PDF RAG Query ─────────────────────────────────────────────────────────

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
        rng = _rng(file_id or "", question, filename or "", _size_hint(metadata))
        title = _stem(filename) if filename else f"document {(file_id or 'unknown')[:8]}"

        if chunks and any(c.strip() for c in chunks):
            clean = [c.strip() for c in chunks if c.strip()]
            snippet_a = clean[0][:120] + ("..." if len(clean[0]) > 120 else "")
            snippet_b = clean[1][:100] + ("..." if len(clean) > 1 and len(clean[1]) > 100 else "") if len(clean) > 1 else ""

            answer = (
                f"Based on the retrieved passages from **{title}**, here is what I found "
                f"regarding \"{question}\":\n\n"
                f"The document states: \"{snippet_a}\""
            )
            if snippet_b:
                answer += f"\n\nAdditionally: \"{snippet_b}\""
            answer += (
                f"\n\nSynthesis: The document {rng.choice(['directly addresses','provides context for','partially covers','elaborates on'])} "
                f"your question. {rng.choice(['The evidence is well-supported.','Further sections may contain related details.','Cross-referencing with other sections is recommended.','This aligns with the document main theme.'])}"
            )

            retrieved = [
                {"id": f"chunk_{i+1}", "text": c[:200], "score": round(rng.uniform(0.82, 0.97), 2)}
                for i, c in enumerate(clean[:5])
            ]
            faithfulness = round(rng.uniform(0.88, 0.97), 2)
            relevance    = round(rng.uniform(0.85, 0.96), 2)
        else:
            answer = (
                f"No readable chunks found for **{title}** for the question \"{question}\". "
                "This can happen if:\n"
                "1. The PDF has not been indexed (upload it via Upload & Analyze first)\n"
                "2. The file contains scanned images without embedded text\n"
                "3. The file is encrypted or protected\n\n"
                "Please upload a text-readable PDF and try again."
            )
            retrieved = []
            faithfulness = 0.45
            relevance    = 0.40

        sources = [
            {
                "page": rng.randint(1, 12),
                "score": round(rng.uniform(0.80, 0.96), 2),
                "text": r["text"] if retrieved else f"Section {i+1} of {title}",
                "source": title,
            }
            for i, r in enumerate((retrieved or [{"text": ""}])[:3])
        ]

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": retrieved,
            "faithfulness_score": faithfulness,
            "relevance_score":    relevance,
            "direct_llm_comparison": (
                f"Without RAG, a generic answer to \"{question}\" would lack the specific "
                f"passages from {title}. RAG grounds the answer in actual document content."
                if retrieved else
                "RAG retrieval returned no chunks — answer is based on general knowledge only."
            ),
            "rag_grounded_answer": answer,
            "hallucination_risk": "low" if faithfulness > 0.80 else "medium",
        }

    # ── Invoice Extraction ────────────────────────────────────────────────────

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
        extracted_text = extracted_text or ""
        fname = filename or file_id or "invoice.pdf"
        rng = _rng(fname, extracted_text[:100], _size_hint(metadata))

        vendors = [
            "Acme Technologies Ltd.",        "BrightPath Solutions Inc.",
            "Nexus Digital Services",        "CoreSystems International",
            "Velocity Cloud Partners",       "PinnacleData Corp.",
            "Meridian Analytics Group",      "Starfield IT Consulting",
            "Summit Enterprise Software",    "BlueWave Digital Ventures",
        ]
        customers = [
            "GlobalTech Solutions Inc.",     "Horizon Ventures LLC",
            "Apex Financial Services",       "Spectrum Innovations Corp.",
            "Unified Systems Group",         "Frontier Analytics Ltd.",
            "Cascade Industries Inc.",       "Zenith Business Services",
        ]
        line_item_catalog = [
            ("Professional Consulting Services", 250.00),
            ("Cloud Infrastructure Setup",        850.00),
            ("Training Workshop (2 days)",        500.00),
            ("Software License — Annual",         1200.00),
            ("API Integration Development",       3200.00),
            ("Data Migration Service",            2100.00),
            ("Security Audit & Compliance",       1750.00),
            ("UI/UX Design Sprint",               4500.00),
            ("DevOps Pipeline Configuration",     980.00),
            ("24/7 Support Package",              600.00),
        ]

        vendor   = rng.choice(vendors)
        customer = rng.choice(customers)

        suffix  = int(hashlib.md5(fname.lower().encode()).hexdigest()[:4], 16) % 9000 + 1000
        inv_num = f"INV-2025-{suffix}"

        day_offset   = rng.randint(0, 120)
        from datetime import date, timedelta
        inv_date  = date(2025, 1, 1) + timedelta(days=day_offset)
        due_date  = inv_date + timedelta(days=rng.choice([15, 30, 45]))

        n_items = rng.randint(2, 4)
        selected_items = rng.sample(line_item_catalog, n_items)
        line_items = []
        for desc, unit_price in selected_items:
            qty   = rng.randint(1, 5)
            total = round(qty * unit_price, 2)
            line_items.append({"description": desc, "quantity": qty, "unit_price": unit_price, "total": total})

        subtotal    = round(sum(li["total"] for li in line_items), 2)
        tax_rate    = rng.choice([0.05, 0.08, 0.10, 0.12])
        tax_amount  = round(subtotal * tax_rate, 2)
        total       = round(subtotal + tax_amount, 2)

        missing = []
        if not extracted_text:
            missing = rng.sample(["purchase_order_number", "payment_terms", "bank_details"], k=rng.randint(0, 2))

        confidence = round(rng.uniform(0.88, 0.98), 2) if extracted_text else round(rng.uniform(0.72, 0.88), 2)

        return {
            "vendor_name":    vendor,
            "customer_name":  customer,
            "invoice_number": inv_num,
            "invoice_date":   inv_date.isoformat(),
            "due_date":       due_date.isoformat(),
            "subtotal":       subtotal,
            "tax_amount":     tax_amount,
            "total_amount":   total,
            "currency":       rng.choice(["USD", "USD", "USD", "EUR", "GBP"]),
            "payment_status": rng.choice(["unpaid", "unpaid", "pending", "partial"]),
            "line_items":     line_items,
            "missing_fields": missing,
            "confidence_score": confidence,
            "safety_note":   "Mock extraction. Values are deterministically generated from filename. Verify against source.",
            "raw_extracted_text": extracted_text[:500] if extracted_text else f"[Mock] No text extracted from {fname}",
        }

    # ── Chart Analysis ────────────────────────────────────────────────────────

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
        question = question or ""
        extracted_text = extracted_text or ""
        fname = filename or file_id or "chart.png"
        rng = _rng(fname, question, extracted_text[:80], _size_hint(metadata))
        title = _stem(fname)

        chart_types  = ["Bar Chart", "Line Chart", "Area Chart", "Scatter Plot", "Pie Chart", "Stacked Bar", "Heatmap", "Histogram"]
        domains      = ["Revenue", "User Growth", "Server Performance", "Conversion Rate", "Error Rate", "Latency (ms)", "CPU Utilization", "API Throughput"]
        time_axes    = ["Q1–Q4 2024", "Jan–Dec 2024", "Week 1–12", "Day 1–30", "Sprint 1–8"]
        trends       = [
            "consistent upward trajectory with accelerating growth in the final period",
            "steady decline after a peak in the middle of the observed range",
            "stable plateau following initial rapid growth — classic S-curve pattern",
            "high volatility with no clear directional trend — possible seasonal noise",
            "sharp spike followed by reversion to mean — typical anomaly pattern",
            "gradual improvement with outlier dip in the third period",
        ]
        categories   = ["Category A", "Category B", "Category C", "Category D"]
        units        = ["$", "%", " req/s", " ms", "K users", " units", ""]
        unit         = rng.choice(units)
        base_val     = rng.uniform(1.2, 8.5)
        peak_val     = round(base_val * rng.uniform(1.3, 2.1), 2)
        low_val      = round(base_val * rng.uniform(0.4, 0.85), 2)
        n_periods    = rng.randint(4, 8)

        chart_type = rng.choice(chart_types)
        domain     = rng.choice(domains)
        time_axis  = rng.choice(time_axes)
        trend      = rng.choice(trends)
        cat_labels = rng.sample(categories, k=min(n_periods, 4))

        data_table = []
        prev = base_val
        for i, label in enumerate(cat_labels):
            val  = round(prev * rng.uniform(0.85, 1.25), 2)
            chg  = f"+{((val/prev)-1)*100:.1f}%" if i > 0 else "baseline"
            data_table.append({"label": label, "value": f"{unit}{val}", "change": chg})
            prev = val

        key_insights = rng.sample([
            f"{domain} shows a {trend.split(' ')[0]} pattern over {time_axis}",
            f"Peak {domain.lower()} of {unit}{peak_val} occurs in {rng.choice(cat_labels)}",
            f"Lowest recorded value is {unit}{low_val} — {rng.choice(['early period','mid-period','final observation'])}",
            f"Average {domain.lower()} across all periods: {unit}{round((peak_val+low_val)/2, 2)}",
            f"Growth rate between first and last period: {round(((peak_val/low_val)-1)*100, 1)}%",
            f"Trend aligns with {rng.choice(['industry average','seasonal pattern','market cycle','historical baseline'])}",
        ], k=4)

        answer = (
            f"The {chart_type} from **{title}** visualizes **{domain}** over {time_axis}. "
            f"The data shows {trend}. "
            f"Peak value is {unit}{peak_val} and the low is {unit}{low_val}."
        )
        if question:
            answer += (
                f"\n\nRegarding your question — \"{question}\": "
                + rng.choice([
                    f"The {chart_type} directly supports this inquiry. The {domain.lower()} data confirms the observed pattern.",
                    f"Based on the visualization, {domain.lower()} {rng.choice(['increased','decreased','stabilized'])} in response to the condition you described.",
                    f"The trend shown is consistent with your question's premise. The peak at {unit}{peak_val} is the key data point.",
                ])
            )

        return {
            "chart_type":   chart_type,
            "title":        f"{domain} — {time_axis}",
            "main_trend":   trend.capitalize(),
            "highest_value": f"{rng.choice(cat_labels)}: {unit}{peak_val}",
            "lowest_value":  f"{rng.choice(cat_labels)}: {unit}{low_val}",
            "key_insights": key_insights,
            "possible_limitations": rng.sample([
                "Chart resolution may obscure minor fluctuations",
                "Underlying raw data not available for verification",
                "Seasonal adjustments are not reflected",
                "Sample size not specified in the visualization",
                "Baseline assumptions may affect interpretation",
            ], k=2),
            "data_table":      data_table,
            "confidence_score": round(rng.uniform(0.80, 0.95), 2),
            "answer":          answer,
            "evaluation":      {"method": "mock_chart_analysis", "domain": domain, "chart_type": chart_type},
        }

    # ── Evaluation ────────────────────────────────────────────────────────────

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        evidence: Optional[List[str]] = None,
        task_type: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        evidence = evidence or []
        task_type = task_type or "visual_chat"
        rng = _rng(question, answer[:80], str(len(evidence)), task_type)

        has_evidence    = len(evidence) > 0
        answer_words    = len((answer or "").split())
        question_words  = set((question or "").lower().split())

        answer_words_set = set((answer or "").lower().split())
        keyword_overlap  = len(question_words & answer_words_set) / max(len(question_words), 1)

        relevance    = round(min(0.97, 0.60 + keyword_overlap * 0.35 + rng.uniform(0.0, 0.08)), 2)
        faithfulness = round(rng.uniform(0.85, 0.97) if has_evidence else rng.uniform(0.52, 0.72), 2)
        completeness = round(min(0.97, 0.50 + min(answer_words, 200) / 200 * 0.47), 2)
        safety       = round(rng.uniform(0.91, 0.99), 2)
        avg          = (relevance + faithfulness + completeness + safety) / 4
        risk         = "low" if avg > 0.82 else ("medium" if avg > 0.68 else "high")

        suggestions = []
        if faithfulness < 0.75:
            suggestions.append("Add supporting evidence or source citations to improve faithfulness.")
        if completeness < 0.70:
            suggestions.append("Expand the answer — consider covering additional aspects of the question.")
        if relevance < 0.75:
            suggestions.append("Ensure the answer directly addresses the specific question asked.")
        if not has_evidence:
            suggestions.append("Include source evidence for better traceability and reduced hallucination risk.")
        if not suggestions:
            suggestions.append("Answer quality is strong. Consider adding a brief confidence statement.")

        return {
            "relevance_score":    relevance,
            "faithfulness_score": faithfulness,
            "completeness_score": completeness,
            "safety_score":       safety,
            "hallucination_risk": risk,
            "missing_evidence":   [] if has_evidence else ["No source evidence provided — claims cannot be independently verified"],
            "risk_explanation": (
                f"Hallucination risk is {risk}. "
                + ("The answer is grounded in the provided evidence." if has_evidence
                   else "Without source evidence, factual claims cannot be validated.")
            ),
            "improvement_suggestions": suggestions,
        }
