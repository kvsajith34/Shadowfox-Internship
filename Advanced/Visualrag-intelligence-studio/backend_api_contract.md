# Backend API Contract — VisualRAG Intelligence Studio

Base URL: `http://localhost:8000`  
All endpoints also available without `/api/v1` prefix (aliases).

---

## Response Envelope

Every endpoint returns:

```json
{
  "success": true,
  "message": "Human-readable message",
  "data": { ... },
  "mock_mode": true,
  "provider": "mock",
  "timestamp": "2024-01-01T12:00:00.000000+00:00"
}
```

On error: `success: false`, `data: null`, `message` contains error detail.

---

## GET /api/v1/health

Health check.

**Response `data`:**
```json
{
  "status": "healthy",
  "app_name": "VisualRAG Intelligence Studio",
  "environment": "development",
  "mock_mode": true,
  "default_provider": "mock",
  "providers": {
    "mock": true,
    "openai": false,
    "gemini": false,
    "anthropic": false,
    "huggingface": false
  },
  "version": "1.0.0"
}
```

---

## POST /api/v1/upload

Upload a file for analysis.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | binary | ✓ | PDF, PNG, JPG, JPEG, TXT, CSV |
| `analysisType` | string | — | `general` (default), `invoice`, `chart`, `rag` |

**Response `data`:**
```json
{
  "file_id": "abc123_report.pdf",
  "filename": "report.pdf",
  "file_type": "pdf",
  "size_bytes": 204800,
  "storage_path": "abc123_report.pdf/report.pdf",
  "analysis_type": "general",
  "status": "uploaded",
  "summary": "First 200 chars of content...",
  "metadata": { "page_count": 12, "original_filename": "report.pdf" },
  "next_suggested_actions": ["visual-chat", "rag-query"]
}
```

---

## POST /api/v1/visual-chat

Analyze an uploaded file via conversational AI.

**Request JSON:**
```json
{
  "file_id": "abc123_image.png",
  "message": "What are the bottlenecks in this diagram?",
  "provider": "mock",
  "history": [
    { "role": "user", "content": "previous question" },
    { "role": "assistant", "content": "previous answer" }
  ]
}
```

| Field | Type | Required | Default |
|---|---|---|---|
| `file_id` | string | — | null |
| `message` | string | ✓ | — |
| `provider` | string | — | `mock` |
| `history` | array | — | `[]` |

**Response `data`:**
```json
{
  "answer": "The database cluster is the primary bottleneck...",
  "evidence": ["Observed 3x load on DB node", "Network latency: 120ms"],
  "evaluation": { "relevance_score": 0.95 },
  "confidence_score": 0.87,
  "safety_notes": "No sensitive content detected",
  "hallucination_risk": "low",
  "suggested_followups": ["What is the throughput?", "How can we scale?"]
}
```

---

## POST /api/v1/pdf-rag-query

Retrieval-augmented question answering over a PDF.

**Request JSON:**
```json
{
  "file_id": "abc123_report.pdf",
  "question": "What were the Q3 revenue findings?",
  "provider": "mock",
  "use_rag": true
}
```

| Field | Type | Required | Default |
|---|---|---|---|
| `file_id` | string | ✓ | — |
| `question` | string | ✓ | — |
| `provider` | string | — | `mock` |
| `use_rag` | boolean | — | `true` |

**Response `data`:**
```json
{
  "answer": "Q3 revenue reached $14.2M, a 12% increase vs Q2...",
  "sources": [{ "page": 3, "score": 0.92, "text": "..." }],
  "retrieved_chunks": [{ "content": "...", "score": 0.88 }],
  "faithfulness_score": 0.96,
  "relevance_score": 0.91,
  "direct_llm_comparison": "Direct LLM also identified the 12% growth figure",
  "rag_grounded_answer": "Based on retrieved chunks: ...",
  "hallucination_risk": "low"
}
```

---

## POST /api/v1/extract-invoice

Extract structured data from an invoice PDF or image.

**Request:** `multipart/form-data`

| Field | Type | Required |
|---|---|---|
| `file` | binary | ✓ |

**Response `data`:**
```json
{
  "vendor_name": "Acme Corporation Ltd.",
  "customer_name": "Tech Startup Inc.",
  "invoice_number": "INV-2024-0042",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "subtotal": 1255.00,
  "tax_amount": 125.50,
  "total_amount": 1380.50,
  "currency": "USD",
  "payment_status": "unpaid",
  "line_items": [
    { "description": "Enterprise Server Rack", "quantity": 2, "unit_price": 450.00, "total": 900.00 }
  ],
  "missing_fields": [],
  "confidence_score": 0.94,
  "safety_note": "No PII detected",
  "raw_extracted_text": "..."
}
```

---

## POST /api/v1/analyze-chart

Analyze a chart or graph image.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | binary | ✓ | PNG, JPG, JPEG |
| `question` | string | — | Specific question about the chart |

**Response `data`:**
```json
{
  "chart_type": "Bar Chart",
  "title": "Q3 Cohort Retention",
  "main_trend": "Declining retention after month 3",
  "highest_value": "Month 1: 98%",
  "lowest_value": "Month 6: 42%",
  "key_insights": ["Strong early retention", "Significant drop at month 3"],
  "possible_limitations": ["Small sample size in month 6"],
  "data_table": [{ "month": 1, "value": 98 }],
  "confidence_score": 0.89,
  "answer": "The chart shows cohort retention declining...",
  "evaluation": {}
}
```

---

## POST /api/v1/evaluate

Evaluate an AI-generated answer.

**Request JSON:**
```json
{
  "question": "What are the main bottlenecks?",
  "answer": "The database cluster is the primary bottleneck...",
  "evidence": ["DB load factor: 3x", "P95 latency: 2.3s"],
  "task_type": "visual_chat",
  "provider": "mock"
}
```

| Field | Type | Required | Default |
|---|---|---|---|
| `question` | string | ✓ | — |
| `answer` | string | ✓ | — |
| `evidence` | array | — | `[]` |
| `task_type` | string | — | `visual_chat` |
| `provider` | string | — | `mock` |

**Response `data`:**
```json
{
  "relevance_score": 0.94,
  "faithfulness_score": 0.91,
  "completeness_score": 0.88,
  "safety_score": 0.99,
  "hallucination_risk": "low",
  "missing_evidence": [],
  "risk_explanation": "Answer is well-grounded in provided evidence",
  "improvement_suggestions": ["Add specific latency numbers"]
}
```

---

## GET /api/v1/metrics

Dashboard metrics.

**Response `data`:**
```json
{
  "totalFiles": 24,
  "filesGrowth": 0.12,
  "queriesHandled": 142,
  "avgFaithfulness": 0.94,
  "hallucinations": 3,
  "providerStatus": { "mock": "Online", "openai": "Offline" },
  "evaluationTrend": [0.85, 0.87, 0.91, 0.94],
  "ragPerformance": { "avg_faithfulness": 0.92, "avg_relevance": 0.88 },
  "safetyAudit": { "passed": 21, "flagged": 3 }
}
```

---

## GET /api/v1/history

Recent analysis history (last 50 records).

**Response `data`:** Array of:
```json
[{
  "id": "vis_abc123",
  "filename": "vis_abc123",
  "type": "visual_chat",
  "provider": "mock",
  "safety": "passed",
  "created_at": "2024-01-01T12:00:00",
  "task_type": "visual_chat",
  "summary": "The database cluster is the primary..."
}]
```

---

## GET /api/v1/reports

Quality and safety report summary.

**Response `data`:**
```json
{
  "summary": {
    "total_analyses": 42,
    "avg_quality_score": 0.94,
    "flagged_count": 3
  },
  "quality_report": {
    "by_type": {
      "invoice": { "avg_time": 1.2, "avg_quality": 0.98 },
      "chart": { "avg_time": 2.5, "avg_quality": 0.94 }
    }
  },
  "safety_audit": {
    "passed": 39,
    "reviewed": 2,
    "flagged": 3
  }
}
```

---

## GET /api/v1/settings

Get current settings.

**Response `data`:**
```json
{
  "default_provider": "mock",
  "default_model": "gpt-4o-mini",
  "vision_model": "gemini-1.5-flash",
  "chunk_size": 512,
  "similarity_threshold": 0.7,
  "mock_mode": true,
  "storage_backend": "local"
}
```

---

## POST /api/v1/settings

Save settings. All fields optional — only provided fields are updated.

**Request JSON:**
```json
{
  "default_provider": "openai",
  "mock_mode": false,
  "chunk_size": 1024,
  "similarity_threshold": 0.75
}
```

**Response `data`:** Same shape as GET /settings.

---

## Unversioned Aliases

All endpoints are also available without `/api/v1/` prefix:

```
GET  /health
POST /upload
POST /visual-chat
POST /pdf-rag-query
POST /extract-invoice
POST /analyze-chart
POST /evaluate
GET  /metrics
GET  /history
GET  /reports
GET  /settings
POST /settings
```
