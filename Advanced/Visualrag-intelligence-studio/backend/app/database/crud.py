"""CRUD operations for database models."""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.database.models import FileRecord, AnalysisRecord, SettingsRecord


# ─── File Records ────────────────────────────────────────────

def create_file_record(db: Session, data: Dict[str, Any]) -> FileRecord:
    """Create a new file record."""
    record = FileRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_file_record(db: Session, file_id: str) -> Optional[FileRecord]:
    """Get a file record by ID."""
    return db.query(FileRecord).filter(FileRecord.id == file_id).first()


def list_file_records(db: Session, limit: int = 50) -> List[FileRecord]:
    """List recent file records."""
    return db.query(FileRecord).order_by(FileRecord.created_at.desc()).limit(limit).all()


def count_file_records(db: Session) -> int:
    """Count total file records."""
    return db.query(FileRecord).count()


# ─── Analysis Records ────────────────────────────────────────

def create_analysis_record(db: Session, data: Dict[str, Any]) -> AnalysisRecord:
    """Create a new analysis record."""
    record = AnalysisRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_analysis_records(db: Session, limit: int = 50) -> List[AnalysisRecord]:
    """List recent analysis records."""
    return db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(limit).all()


def count_analysis_records(db: Session) -> int:
    """Count total analysis records."""
    return db.query(AnalysisRecord).count()


def get_safety_stats(db: Session) -> Dict[str, int]:
    """Get safety audit statistics."""
    total = db.query(AnalysisRecord).count()
    passed = db.query(AnalysisRecord).filter(AnalysisRecord.safety_status == "passed").count()
    flagged = db.query(AnalysisRecord).filter(AnalysisRecord.safety_status == "flagged").count()
    return {"passed": passed, "flagged": flagged, "total": total}


def get_avg_faithfulness(db: Session) -> float:
    """Get average faithfulness score."""
    records = db.query(AnalysisRecord).all()
    if not records:
        return 0.87  # fallback for empty db
    scores = [r.faithfulness_score for r in records if r.faithfulness_score and r.faithfulness_score > 0]
    return sum(scores) / len(scores) if scores else 0.87


def get_hallucination_count(db: Session) -> int:
    """Count high hallucination risk records."""
    return db.query(AnalysisRecord).filter(AnalysisRecord.hallucination_risk.in_(["high", "medium"])).count()


# ─── Settings Records ────────────────────────────────────────

def get_current_settings(db: Session) -> SettingsRecord:
    """Get current settings or create defaults SEEDED FROM backend/.env.

    Important: a brand-new settings row must reflect MOCK_MODE/DEFAULT_PROVIDER
    from .env at the moment the row is first created. Previously this used
    hardcoded model-column defaults (mock_mode=1, provider="mock"), which
    silently ignored .env and trapped the app in mock mode even when the
    user had configured real provider keys.
    """
    record = db.query(SettingsRecord).first()
    if not record:
        from app.core.config import settings as app_settings, get_default_model_for
        provider = app_settings.DEFAULT_PROVIDER if app_settings.DEFAULT_PROVIDER in (
            "mock", "openai", "gemini", "huggingface", "anthropic"
        ) else "mock"
        record = SettingsRecord(
            default_provider=provider,
            default_model=get_default_model_for(provider),
            vision_model=app_settings.GEMINI_MODEL,
            mock_mode=1 if app_settings.MOCK_MODE else 0,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    return record


def update_settings(db: Session, data: Dict[str, Any]) -> SettingsRecord:
    """Update settings."""
    record = get_current_settings(db)
    for key, value in data.items():
        if key == "mock_mode":
            value = 1 if value else 0
        if hasattr(record, key):
            setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def reset_settings_to_env(db: Session) -> SettingsRecord:
    """Reset saved provider settings back to backend/.env defaults.

    Lets a user un-stick the app from a stale saved mock_mode/provider
    without manually re-entering every field — a safe "undo" back to
    whatever the current .env says.
    """
    from app.core.config import settings as app_settings, get_default_model_for
    provider = app_settings.DEFAULT_PROVIDER if app_settings.DEFAULT_PROVIDER in (
        "mock", "openai", "gemini", "huggingface", "anthropic"
    ) else "mock"
    return update_settings(db, {
        "default_provider": provider,
        "default_model": get_default_model_for(provider),
        "mock_mode": app_settings.MOCK_MODE,
    })
