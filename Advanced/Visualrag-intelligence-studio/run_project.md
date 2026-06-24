# Run Project Guide — VisualRAG Intelligence Studio

Quick reference for running the project locally, in Docker, or for testing.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| npm | 9+ | Bundled with Node |
| Docker _(optional)_ | 24+ | https://docker.com |

---

## 1. Backend — Local (Fastest)

```bash
# Step 1 — Enter backend directory
cd backend

# Step 2 — Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Step 3 — Install dependencies
pip install -r requirements.txt

# Step 4 — Create .env from example
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env

# Step 5 — Start the server (--host 0.0.0.0 lets LAN devices reach the backend)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend ready at:** http://localhost:8000  
**API docs (Swagger):** http://localhost:8000/docs  
**Health check:** http://localhost:8000/api/v1/health

---

## 2. Frontend — Local

Open a second terminal:

```bash
# Step 1 — Enter frontend directory
cd frontend

# Step 2 — Install dependencies
npm install

# Step 3 — Create .env from example
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env

# Step 4 — Start dev server
npm run dev
```

**Frontend ready at:** http://localhost:5173

---

## 3. Run Both (Parallel)

From the project root, open two terminals:

```bash
# Terminal 1 — Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

---

## 4. Docker (Full Stack)

```bash
# From project root
cp backend/.env.example backend/.env

# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View backend logs
docker-compose logs -f backend

# Stop all
docker-compose down
```

Services started:
- `visualrag-backend` → http://localhost:8000
- `visualrag-db` (PostgreSQL) → localhost:5432
- `visualrag-chromadb` → http://localhost:8001
- `visualrag-minio` → http://localhost:9000 (console: 9001)
- `visualrag-redis` → localhost:6379

---

## 5. Tests

```bash
cd backend

# Activate venv first
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Run all tests
pytest -q

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_health.py -v
pytest tests/test_upload.py -v
pytest tests/test_visual_chat.py -v

# Run with coverage
pip install pytest-cov
pytest --cov=app tests/ -q
```

---

## 6. Frontend Build

```bash
cd frontend

# Type check
npm run lint

# Production build
npm run build

# Preview production build
npm run preview
```

---

## 7. Smoke Test Script

```bash
cd backend
source venv/bin/activate
python scripts/smoke_test.py
```

---

## 8. Seed Demo Data

```bash
cd backend
source venv/bin/activate
python scripts/seed_demo_data.py
```

---

## Environment Quick Reference

### Mock Mode (default — no API keys needed)
```env
# backend/.env
MOCK_MODE=true
DEFAULT_PROVIDER=mock
```

### OpenAI Mode
```env
MOCK_MODE=false
DEFAULT_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### Gemini Mode
```env
MOCK_MODE=false
DEFAULT_PROVIDER=gemini
GOOGLE_API_KEY=AIza...
```

---

## Common Issues

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside venv |
| `CORS error` in browser | Ensure backend runs on port 8000 with `--host 0.0.0.0` |
| Frontend shows "Mock Mode" badge | Backend not reachable — start backend first |
| `sqlite3.OperationalError` | Delete `visualrag.db` and restart backend |
| Port 5173 in use | Change in `vite.config.ts` or kill the process |
| Port 8000 in use | Use `uvicorn main:app --host 0.0.0.0 --port 8001` and set `VITE_API_BASE_URL=` in `frontend/.env` (proxy rewires automatically) |
| Network URL uploads fail | Leave `VITE_API_BASE_URL=` empty in `frontend/.env` — Vite proxy handles routing |
| Network URL CORS error | Add `http://<your-ip>:5173` to `CORS_ORIGINS` in `backend/.env` |

---

## Network URL (LAN) Setup

When you share the Vite network URL (e.g. `http://192.168.x.x:5173`) with another device:

1. Backend must bind to all interfaces: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Frontend must bind to all interfaces too: `npm run dev -- --host 0.0.0.0` (the project's `package.json` already runs `vite --host=0.0.0.0` by default, so plain `npm run dev` already works — the explicit flag is only needed if you've customized the script)
3. Leave `VITE_API_BASE_URL=` **empty** in `frontend/.env` (relative URLs, Vite proxy forwards them)
4. The browser on the remote device sends `/api/*` to the Vite server, which proxies it to `localhost:8000` — so CORS is never an issue in this mode

### Option A — Vite proxy (no CORS setup needed)

This is the default and requires no extra configuration — see steps 1-4 above.

### Option B — Custom Backend URL (Settings page)

Use this when the frontend and backend run on **different machines**, or when there's no Vite dev server in front of the frontend (e.g. a static/deployed build) — so there's no proxy to rely on.

1. Open **Settings → Network Connection**
2. Toggle **Use Custom Backend URL** on
3. Enter the backend's full URL, e.g. `http://10.155.121.181:8000`
4. Click **Test Connection** — it calls the backend's `/api/v1/health` directly and shows success/error
5. Saved to this browser's `localStorage` — takes effect on the very next request, no rebuild or reload required

For this mode, the backend's CORS must explicitly allow the frontend's origin:
```env
# backend/.env
CORS_ORIGINS=["http://localhost:5173","http://10.155.121.181:5173"]
```

In development (`APP_ENV` not set to `production`), the backend also automatically allows common private-LAN origins via a regex pattern — `localhost`, `127.0.0.1`, `10.x.x.x`, `172.16-31.x.x`, and `192.168.x.x` on ports `5173`/`3000` — so you often don't need to add your exact IP manually. This regex is **never** active in production and is always combined with (not a replacement for) the explicit `CORS_ORIGINS` list; `allow_origins=["*"]` is never used together with credentials.

---

## Diagnosing Provider / Mock Mode Issues

If real providers (OpenAI/Gemini/Hugging Face) aren't activating as expected:

```
GET /api/v1/provider-debug
```

Returns a secrets-free snapshot (booleans and short strings only):
```json
{
  "mock_mode_raw": "false",
  "mock_mode_parsed": false,
  "default_provider": "gemini",
  "selected_provider": "gemini",
  "active_provider": "gemini",
  "selected_model": "gemini-2.5-flash",
  "api_key_status": { "openai": false, "gemini": true, "huggingface": false },
  "fallback_reason": null,
  "last_fallback_reason": null,
  "last_provider_error_type": null,
  "provider_service_available": { "openai": true, "gemini": true, "huggingface": true, "anthropic": true },
  "service_methods_available": {
    "openai_visual_chat": true, "gemini_visual_chat": true,
    "huggingface_visual_chat": true, "mock_visual_chat": true
  }
}
```

`fallback_reason` (pre-call gating) is `null` unless mock mode is on, the key is missing, or the SDK isn't installed — one of: `mock mode enabled`, `selected provider API key missing`, `provider SDK error`. `last_fallback_reason` / `last_provider_error_type` instead show the most recent *live-call* failure (e.g. `"OpenAI rate limit or quota reached..."` / `"RateLimitError"`, or `"Gemini model not found..."` / `"NotFound"`) — purely informational. **A live-call failure never permanently pins the provider to mock** — it falls back for that one request only, and the next request tries the real provider again. The Settings page's Debug Info panel shows the same data.

**Real-provider checklist:**
1. Add the key to `backend/.env` (`OPENAI_API_KEY`, `GOOGLE_API_KEY`, or `HF_TOKEN`)
2. Set `MOCK_MODE=false` and `GEMINI_MODEL=gemini-2.5-flash` (or your preferred current model)
3. Restart the backend
4. Select the provider in Settings and save

If the provider's live API call fails for any reason (bad key, quota, model not found, network), the request **automatically falls back to a mock response for that request only** rather than crashing — check `/api/v1/provider-debug`'s `last_fallback_reason` to see why. Gemini specifically retries `gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.0-flash` automatically when the configured model returns `NotFound`, before falling back to mock.
