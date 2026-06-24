# VisualRAG Intelligence Studio

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange)


A full-stack multimodal AI document intelligence application. Upload PDFs and images, ask questions with Retrieval-Augmented Generation, extract structured data from invoices, analyze charts, and evaluate AI-generated answers — all from a single interface with switchable AI providers.

---

## Table of Contents

1. [Key Features](#key-features)
2. [System Architecture](#system-architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [AI Provider Support](#ai-provider-support)
6. [Current Status](#current-status)
7. [Known Limitations](#known-limitations)
8. [Installation and Setup](#installation-and-setup)
   - [Backend Setup](#backend-setup)
   - [Frontend Setup](#frontend-setup)
9. [Environment Variables](#environment-variables)
10. [Running the Project](#running-the-project)
11. [Testing the Application](#testing-the-application)
12. [API Endpoints](#api-endpoints)
13. [Screenshots](#screenshots)
14. [Future Improvements](#future-improvements)
15. [Security Notes](#security-notes)
16. [License](#license)
17. [Author](#author)

---

## Key Features

- **PDF RAG Chat** — chunk, embed, and query PDFs with vector-store retrieval (ChromaDB)
- **Upload & Analyze** — general document intelligence for PDFs, images, TXT, and CSV files
- **Visual Chat** — conversational AI over uploaded images and documents
- **Invoice Extractor** — structured field extraction from invoice images/PDFs
- **Chart Analyzer** — trend, insight, and data-table extraction from chart images
- **Evaluation Lab** — score AI answers on relevance, faithfulness, completeness, and safety
- **Dashboard & Metrics** — live stats on files processed, queries handled, and quality scores
- **Reports** — quality and safety audit summaries
- **Provider Switching** — toggle between Gemini, OpenAI, Hugging Face, Anthropic, and Mock from the Settings page, with automatic fallback
- **Mock Mode** — fully offline fallback that requires no API keys

---

## System Architecture

```
Browser (React/Vite :5173)
        │
        │  HTTP / Vite proxy
        ▼
FastAPI Backend (:8000)
   ├── Provider Router  ──► Gemini / OpenAI / HuggingFace / Anthropic / Mock
   ├── RAG Service      ──► ChromaDB (vector store) + SQLite (metadata)
   ├── Document Parser  ──► PyMuPDF + pdfplumber
   ├── Storage Service  ──► Local filesystem (S3/MinIO optional)
   └── Database Layer   ──► SQLAlchemy + SQLite (PostgreSQL optional)
```

The Vite dev server proxies all `/api/*` requests to the backend, so the frontend never needs to know the backend's IP — this also makes LAN access work automatically.

---

## Tech Stack

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| Vite | 6 | Dev server and build tool |
| TypeScript | 5.8 | Type safety |
| Tailwind CSS | 4 | Styling |
| Axios | 1.x | HTTP client |
| React Router DOM | 7 | Client-side routing |
| Recharts | 3 | Dashboard charts |
| Lucide React | 0.546 | Icons |
| Motion | 12 | Animations |

### Backend

| Technology | Version | Purpose |
|---|---|---|
| FastAPI | 0.115 | API framework |
| Uvicorn | 0.34 | ASGI server |
| Pydantic v2 | 2.10 | Schema validation |
| SQLAlchemy | 2.0 | ORM / database layer |
| SQLite | built-in | Default metadata store |
| ChromaDB | 0.5 | Vector store for RAG |
| PyMuPDF | 1.25 | PDF parsing |
| pdfplumber | 0.11 | PDF text extraction |
| google-generativeai | 0.8 | Gemini provider |
| openai | 1.58 | OpenAI provider |
| anthropic | 0.42 | Anthropic provider |
| huggingface-hub | 0.27 | Hugging Face provider |
| scikit-learn | 1.6 | Embedding utilities |
| Pillow | 11 | Image handling |

---

## Project Structure

```
visualrag-intelligence-studio/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── Dockerfile
│   ├── .env.example               # Copy to .env and fill in keys
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/                # Versioned routes (/api/v1/...)
│   │   │   │   ├── health_routes.py
│   │   │   │   ├── upload_routes.py
│   │   │   │   ├── rag_routes.py
│   │   │   │   ├── visual_chat_routes.py
│   │   │   │   ├── invoice_routes.py
│   │   │   │   ├── chart_routes.py
│   │   │   │   ├── evaluation_routes.py
│   │   │   │   ├── metrics_routes.py
│   │   │   │   ├── history_routes.py
│   │   │   │   ├── reports_routes.py
│   │   │   │   └── settings_routes.py
│   │   │   └── aliases.py         # Unversioned aliases (/upload, /health, ...)
│   │   ├── core/
│   │   │   ├── config.py          # Settings loaded from backend/.env
│   │   │   └── security.py
│   │   ├── database/
│   │   │   ├── db.py
│   │   │   ├── models.py
│   │   │   └── crud.py
│   │   ├── services/
│   │   │   ├── provider_router.py # Runtime provider switching + fallback logic
│   │   │   ├── gemini_service.py
│   │   │   ├── openai_service.py
│   │   │   ├── anthropic_service.py
│   │   │   ├── huggingface_service.py
│   │   │   ├── mock_ai_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── document_parser.py
│   │   │   ├── storage_service.py
│   │   │   ├── invoice_service.py
│   │   │   ├── chart_service.py
│   │   │   ├── evaluation_service.py
│   │   │   ├── metrics_service.py
│   │   │   └── report_service.py
│   │   ├── vectorstore/
│   │   │   ├── chroma_store.py
│   │   │   └── embeddings.py
│   │   ├── schemas/               # Pydantic request/response models
│   │   └── utils/
│   ├── tests/                     # pytest test suite
│   └── scripts/
│       ├── smoke_test.py
│       └── seed_demo_data.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── PdfRagChat.tsx
│   │   │   ├── UploadAnalyze.tsx
│   │   │   ├── VisualChat.tsx
│   │   │   ├── InvoiceExtractor.tsx
│   │   │   ├── ChartAnalyzer.tsx
│   │   │   ├── EvaluationLab.tsx
│   │   │   ├── Reports.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   ├── api/
│   │   │   └── client.ts          # Typed API client
│   │   └── data/
│   │       └── mockData.ts
│   ├── .env.example               # Copy to .env — only VITE_API_BASE_URL goes here
│   ├── package.json
│   └── vite.config.ts
├── .github/
│   └── workflows/
│       └── backend-ci.yml         # GitHub Actions CI
├── docker-compose.yml
├── backend_api_contract.md
├── run_project.md
├── screenshots/                   # Add screenshots here
└── reports/                       # Generated reports saved here
```

---

## AI Provider Support

| Provider | Status | Notes |
|---|---|---|
| **Google Gemini** | ✅ Working | Recommended provider for demos. Primary model: `gemini-2.5-flash`. Automatically retries `gemini-2.5-flash-lite` → `gemini-2.0-flash` if a model is unavailable. Falls back to mock if quota is reached. |
| **OpenAI** | ⚠️ Configured, limited | API key is detected and the API is reached, but currently returns 429 rate-limit / quota errors. Falls back to mock mode. |
| **Hugging Face** | ⚠️ Configured, variable | Token is detected. Requests may fail depending on selected model or endpoint availability. Falls back to mock mode. |
| **Anthropic** | 🔧 Optional | `anthropic_service.py` is implemented. Requires a valid `CLAUDE_API_KEY` in `backend/.env`. Not configured by default. |
| **Mock** | ✅ Always available | Fully offline fallback. No API keys required. Used automatically when a real provider fails or when `MOCK_MODE=true`. |

Provider selection and fallback can be inspected in real time at:

```
GET http://localhost:8000/api/v1/provider-debug
```

This endpoint returns only booleans and short strings — it never exposes actual key values.

---

## Current Status

| Component | Status |
|---|---|
| Backend (Uvicorn on port 8000) | ✅ Running |
| Frontend (Vite on port 5173) | ✅ Running |
| File upload | ✅ Working |
| PDF text extraction and RAG chunking | ✅ Working |
| ChromaDB vector store (real provider mode) | ✅ Working |
| Mock fallback mode | ✅ Working |
| Provider switching from Settings page | ✅ Working |
| Gemini summarization and RAG | ✅ Working (primary recommended provider) |
| OpenAI | ⚠️ Falls back to mock (quota/rate-limit) |
| Hugging Face | ⚠️ Falls back to mock (model/endpoint availability) |
| Anthropic | 🔧 Requires `CLAUDE_API_KEY` to activate |

---

## Known Limitations

- **Gemini list-response warnings** — some detailed or list-style prompts may cause a backend warning when Gemini returns a Python list and the database expects a string. The response still succeeds; only a log warning is produced.
- **OpenAI quota** — the app currently receives 429 errors from the OpenAI API and falls back to mock. This resolves once API quota is available.
- **Hugging Face availability** — requests may fail depending on the selected model (`HF_MODEL` in `.env`) or Hugging Face Inference API endpoint availability.
- **Anthropic not configured by default** — `CLAUDE_API_KEY` must be added to `backend/.env` to activate this provider.
- **ChromaDB telemetry warnings** — ChromaDB may log telemetry warnings on startup. These do not affect functionality.
- **Response quality** — all real-provider responses depend on valid API keys, available quota, model availability, and provider-side rate limits. Mock mode always responds but with static, non-document-aware answers.

---

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher and npm
- Git

### Clone the Repository

```bash
git clone https://github.com/kvsajith34/Shadowfox-Internship.git
cd Advanced/visualrag-intelligence-studio
```

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `backend/.env` and fill in your API keys (see [Environment Variables](#environment-variables)).

### Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env
```

The default `frontend/.env` sets `VITE_API_BASE_URL=` (empty), which enables the Vite proxy. **Do not add API keys to the frontend `.env`.**

---

## Environment Variables

### `backend/.env`

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment name |
| `MOCK_MODE` | `true` | `false` to use real providers; `true` for offline/demo mode |
| `DEFAULT_PROVIDER` | `mock` | Active provider: `gemini`, `openai`, `huggingface`, `anthropic`, or `mock` |
| `GOOGLE_API_KEY` | _(empty)_ | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `OPENAI_API_KEY` | _(empty)_ | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `HF_TOKEN` | _(empty)_ | Hugging Face token |
| `HF_MODEL` | `Qwen/Qwen2.5-VL-3B-Instruct` | Hugging Face model ID |
| `CLAUDE_API_KEY` | _(empty)_ | Anthropic API key (optional) |
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` | Anthropic model name |
| `DATABASE_URL` | `sqlite:///./visualrag.db` | Database connection string |
| `CHROMA_DIR` | `./chroma_db` | ChromaDB storage path |
| `UPLOAD_DIR` | `./uploads` | Uploaded file storage path |
| `MAX_UPLOAD_MB` | `50` | Maximum upload size in MB |
| `CORS_ORIGINS` | `["http://localhost:5173", ...]` | Allowed frontend origins |

Example `backend/.env` for Gemini:

```env
MOCK_MODE=false
DEFAULT_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
HF_TOKEN=your_huggingface_token_here
HF_MODEL=Qwen/Qwen2.5-VL-3B-Instruct
```

### `frontend/.env`

| Variable | Value | Description |
|---|---|---|
| `VITE_API_BASE_URL` | _(empty for local dev)_ | Leave empty to use Vite proxy. Set to full backend URL for deployed environments. |

```env
VITE_API_BASE_URL=
```

> **Never commit `backend/.env` or `frontend/.env` to GitHub.** Both are excluded by `.gitignore`.

---

## Running the Project

### Local Development

**Terminal 1 — Backend:**

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Interactive API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/v1/health |
| Provider debug | http://localhost:8000/api/v1/provider-debug |

### LAN / Network Access

Both servers already bind to `0.0.0.0`. Once running, any device on your local network can reach the app using your machine's IP:

```
http://<your-local-ip>:5173          # Frontend
http://<your-local-ip>:8000/api/v1/health  # Backend health
```

> If you access the frontend from a different machine (not using the Vite proxy), set `VITE_API_BASE_URL=http://<your-local-ip>:8000` in `frontend/.env` and add `http://<your-local-ip>:5173` to `CORS_ORIGINS` in `backend/.env`.

---

## Testing the Application

### Backend Tests

```bash
cd backend
venv\Scripts\activate
pytest -q
```

### Frontend Type Check and Build

```bash
cd frontend
npm run lint
npm run build
```

### Manual Demo Workflow

1. Start the backend (Terminal 1).
2. Start the frontend (Terminal 2).
3. Open **Dashboard** at http://localhost:5173 to confirm metrics load.
4. Go to **Settings** → select **Gemini** as the provider → save.
5. Go to **Upload & Analyze** → upload a PDF or image.
6. Go to **PDF RAG Chat** → select your uploaded file → ask a question.
7. Go to **Visual Chat** → upload an image → start a conversation.
8. Go to **Invoice Extractor** → upload an invoice image or PDF.
9. Go to **Chart Analyzer** → upload a chart image → optionally type a specific question.
10. Go to **Evaluation Lab** → enter a question, answer, and evidence → run evaluation.
11. Go to **Reports** → review quality and safety summaries.
12. Visit `http://localhost:8000/api/v1/provider-debug` to inspect the active provider state.

> **Recommended demo provider: Gemini.** Set `DEFAULT_PROVIDER=gemini` and `MOCK_MODE=false` in `backend/.env`.

---

## API Endpoints

All endpoints are available under `/api/v1/` (versioned) and also as unversioned aliases (e.g., `/health`, `/upload`).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check and provider status |
| `GET` | `/api/v1/provider-debug` | Detailed provider configuration (safe — no key values) |
| `POST` | `/api/v1/upload` | Upload a file (PDF, PNG, JPG, TXT, CSV) |
| `POST` | `/api/v1/visual-chat` | Conversational AI over an uploaded file |
| `POST` | `/api/v1/pdf-rag-query` | RAG-based question answering over a PDF |
| `POST` | `/api/v1/extract-invoice` | Structured field extraction from invoice files |
| `POST` | `/api/v1/analyze-chart` | Trend and insight extraction from chart images |
| `POST` | `/api/v1/evaluate` | Score an AI answer on relevance, faithfulness, completeness, and safety |
| `GET` | `/api/v1/metrics` | Dashboard statistics |
| `GET` | `/api/v1/history` | Recent analysis history (last 50 records) |
| `GET` | `/api/v1/reports` | Quality and safety report summary |
| `GET` | `/api/v1/settings` | Get current provider and configuration |
| `POST` | `/api/v1/settings` | Update provider, model, and RAG settings |

Full request/response schemas are available at `/docs` (Swagger UI) when the backend is running.

---

## Future Improvements

- Activate and test Anthropic (Claude) provider once a key is available
- Resolve OpenAI quota to enable full GPT-4o-mini testing
- Add PostgreSQL support for production deployments (already in `DATABASE_URL` config)
- Add S3/MinIO storage backend (config already present)
- Stream AI responses to the frontend for long documents
- Add user authentication and per-user session history
- Expand the test suite to cover RAG and provider-router paths
- Add Docker Compose one-command startup instructions after local testing is complete
- Add screenshots to the `screenshots/` directory

---

## Security Notes

- **Never commit API keys.** Both `backend/.env` and `frontend/.env` are excluded in `.gitignore`.
- **API keys belong only in `backend/.env`.** The frontend `.env` must contain only `VITE_API_BASE_URL`.
- The `/api/v1/provider-debug` endpoint returns only booleans and short strings. It never exposes actual key values.
- The backend validates CORS origins. Do not set `CORS_ORIGINS=["*"]` in production.
- Add the following to your `.gitignore` if not already present:

```
backend/.env
frontend/.env
venv/
node_modules/
frontend/dist/
__pycache__/
*.db
*.sqlite3
backend/uploads/
backend/chroma_db/
```

---

## Author

**Venkata Sai Ajith Kancheti**  
B.Tech CSE (AI/ML) — Apollo University  
GitHub: [@kvsajith34](https://github.com/kvsajith34)
