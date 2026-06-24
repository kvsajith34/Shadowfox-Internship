"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.database.db import init_db, ensure_upload_dir

# Import route routers
from app.api.v1.health_routes import router as health_router
from app.api.v1.upload_routes import router as upload_router
from app.api.v1.visual_chat_routes import router as visual_chat_router
from app.api.v1.rag_routes import router as rag_router
from app.api.v1.invoice_routes import router as invoice_router
from app.api.v1.chart_routes import router as chart_router
from app.api.v1.evaluation_routes import router as evaluation_router
from app.api.v1.metrics_routes import router as metrics_router
from app.api.v1.history_routes import router as history_router
from app.api.v1.reports_routes import router as reports_router
from app.api.v1.settings_routes import router as settings_router
from app.api.aliases import router as aliases_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    setup_logging()
    logger.info("Starting %s (env=%s, mock=%s)", settings.APP_NAME, settings.APP_ENV, settings.MOCK_MODE)
    ensure_upload_dir()
    init_db()
    # Restore saved provider/mock_mode from DB into in-memory runtime state
    # so that settings saved in a previous session take effect immediately.
    try:
        from app.database.db import get_session_local
        from app.services.provider_router import load_runtime_state_from_db
        SessionLocal = get_session_local()
        with SessionLocal() as db:
            load_runtime_state_from_db(db)
    except Exception as e:
        logger.warning("Could not restore runtime provider state: %s", e)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready FastAPI backend for multimodal AI document analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
# allow_origins: explicit list from CORS_ORIGINS (always applied).
# allow_origin_regex: ALSO accept common private-LAN IP origins on ports
# 5173/3000 — but ONLY outside production, and used alongside (not instead
# of) the explicit list. allow_credentials=True + allow_origin_regex is safe
# here because the regex is still a finite, scoped pattern — never "*".
_lan_regex = (
    r"^http://(localhost|127\.0\.0\.1|"
    r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|"
    r"192\.168\.\d{1,3}\.\d{1,3}):(5173|3000)$"
    if settings.APP_ENV != "production" else None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_origin_regex=_lan_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Versioned API Routes (/api/v1/...) ─────────────────────
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(visual_chat_router, prefix="/api/v1", tags=["Visual Chat"])
app.include_router(rag_router, prefix="/api/v1", tags=["PDF RAG"])
app.include_router(invoice_router, prefix="/api/v1", tags=["Invoice Extraction"])
app.include_router(chart_router, prefix="/api/v1", tags=["Chart Analysis"])
app.include_router(evaluation_router, prefix="/api/v1", tags=["Evaluation"])
app.include_router(metrics_router, prefix="/api/v1", tags=["Metrics"])
app.include_router(history_router, prefix="/api/v1", tags=["History"])
app.include_router(reports_router, prefix="/api/v1", tags=["Reports"])
app.include_router(settings_router, prefix="/api/v1", tags=["Settings"])

# ─── Unversioned Aliases (/health, /upload, ...) ────────────
app.include_router(aliases_router, tags=["Aliases"])


# ─── Root endpoint ───────────────────────────────────────────
@app.get("/")
async def root():
    """API root — redirect to docs or return info."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "mock_mode": settings.MOCK_MODE,
        "message": "Welcome to VisualRAG Intelligence Studio API. Visit /docs for interactive documentation.",
    }
