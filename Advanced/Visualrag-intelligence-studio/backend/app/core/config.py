"""Core configuration module.

Key reliability fixes:
  - backend/.env is loaded from an ABSOLUTE path (derived from this file's
    location), so it loads correctly no matter what directory `uvicorn` is
    started from.
  - MOCK_MODE is parsed with an explicit validator (not `bool(os.getenv(...))`,
    which incorrectly treats the string "false" as truthy).
  - GOOGLE_API_KEY / HF_TOKEN support common alias env var names as fallbacks.
"""
import json
import os
from pathlib import Path
from typing import Any, List, Optional

from dotenv import load_dotenv
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings

# ─── Reliable .env loading ─────────────────────────────────────────────────────
# Resolve backend/.env relative to THIS FILE (app/core/config.py -> backend/),
# not relative to the process's current working directory. This guarantees
# the .env loads correctly whether uvicorn is started from `backend/`,
# the repo root, or anywhere else.
BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BACKEND_DIR / ".env"

# Populate os.environ from backend/.env before Settings() reads anything.
# override=False: real shell-exported env vars always win over the .env file.
load_dotenv(dotenv_path=ENV_PATH, override=False)


def env_file_exists() -> bool:
    """Whether backend/.env was found on disk at startup."""
    return ENV_PATH.exists()


def get_mock_mode_raw() -> str:
    """Raw (unparsed) MOCK_MODE value as seen in the environment — for debug only."""
    return os.environ.get("MOCK_MODE", "<unset, defaults to true>")


def _parse_bool_env(value: Any, default: bool = True) -> bool:
    """Explicit, safe string -> bool parsing. Avoids the bool('false') == True pitfall."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    s = str(value).strip().lower()
    if s in ("false", "0", "no", "off", "n", "f", ""):
        return False
    if s in ("true", "1", "yes", "on", "y", "t"):
        return True
    return default  # unknown value -> safe default (mock)


# ─── Settings ───────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    """Application settings loaded from environment variables / backend/.env."""

    APP_NAME: str = "VisualRAG Intelligence Studio"
    APP_ENV: str = "development"
    MOCK_MODE: bool = True
    DEFAULT_PROVIDER: str = "mock"

    # ── AI Provider Keys (primary names) ────────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None

    # ── AI Provider Key aliases (fallback names, never used directly) ───────────
    # GEMINI_API_KEY -> fills GOOGLE_API_KEY if GOOGLE_API_KEY is empty.
    # HUGGINGFACE_API_KEY / HUGGINGFACE_TOKEN -> fill HF_TOKEN if HF_TOKEN is empty.
    GEMINI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None

    # AI Models
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    HF_MODEL: str = "Qwen/Qwen2.5-VL-3B-Instruct"
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # Database
    DATABASE_URL: str = "sqlite:///./visualrag.db"
    POSTGRES_USER: str = "visualrag"
    POSTGRES_PASSWORD: str = "visualrag_password"
    POSTGRES_DB: str = "visualrag_db"

    # Vector Store
    CHROMA_DIR: str = "./chroma_db"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 50
    STORAGE_BACKEND: str = "local"

    # S3 / MinIO
    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "visualrag"
    S3_SECRET_KEY: str = "visualrag_password"
    S3_BUCKET: str = "visualrag-uploads"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173","http://127.0.0.1:3000","http://127.0.0.1:5173"]'

    model_config = {"env_file": str(ENV_PATH), "env_file_encoding": "utf-8", "extra": "ignore"}

    # ── Validators ───────────────────────────────────────────────────────────────

    @field_validator("MOCK_MODE", mode="before")
    @classmethod
    def _validate_mock_mode(cls, v: Any) -> bool:
        """Explicit parsing so MOCK_MODE=false reliably becomes Python False.

        Using bool(os.getenv("MOCK_MODE")) is a classic bug: bool("false") is
        True in Python because any non-empty string is truthy. This validator
        parses the actual string content instead.
        """
        return _parse_bool_env(v, default=True)

    @model_validator(mode="after")
    def _apply_provider_key_aliases(self) -> "Settings":
        """Fill primary key fields from alias env vars when the primary is unset."""
        if not self.GOOGLE_API_KEY and self.GEMINI_API_KEY:
            self.GOOGLE_API_KEY = self.GEMINI_API_KEY
        if not self.HF_TOKEN:
            if self.HUGGINGFACE_API_KEY:
                self.HF_TOKEN = self.HUGGINGFACE_API_KEY
            elif self.HUGGINGFACE_TOKEN:
                self.HF_TOKEN = self.HUGGINGFACE_TOKEN
        return self

    # ── Helpers ──────────────────────────────────────────────────────────────────

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from JSON string or comma-separated."""
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return [o.strip() for o in str(self.CORS_ORIGINS).split(",") if o.strip()]

    def get_effective_database_url(self) -> str:
        """Return PostgreSQL URL in Docker, SQLite locally."""
        if os.environ.get("DATABASE_URL"):
            return os.environ["DATABASE_URL"]
        if self.APP_ENV in ("production", "docker"):
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db:5432/{self.POSTGRES_DB}"
        return self.DATABASE_URL

    def is_provider_available(self, provider: str) -> bool:
        """Check if a given provider has its API key configured."""
        if self.MOCK_MODE:
            return provider == "mock"
        key_map = {
            "openai": self.OPENAI_API_KEY,
            "gemini": self.GOOGLE_API_KEY,
            "anthropic": self.CLAUDE_API_KEY,
            "huggingface": self.HF_TOKEN,
            "mock": "always",
        }
        return bool(key_map.get(provider))


settings = Settings()

# Ordered fallback list tried by GeminiService when the configured
# GEMINI_MODEL (settings.GEMINI_MODEL) raises NotFound — i.e. the model name
# is unavailable/retired for the configured API version/region. The first
# entry that succeeds is used; which one succeeded is logged.
GEMINI_MODEL_FALLBACKS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]


def get_default_model_for(provider: str) -> str:
    """Sensible default model name for a given provider, sourced from .env."""
    if provider == "openai":
        return settings.OPENAI_MODEL
    if provider == "gemini":
        return settings.GEMINI_MODEL
    if provider == "huggingface":
        return settings.HF_MODEL
    if provider == "anthropic":
        return settings.CLAUDE_MODEL
    return "mock-visualrag"
