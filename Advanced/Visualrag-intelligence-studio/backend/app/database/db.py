"""Database setup and session management."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        db_url = settings.get_effective_database_url()
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_engine(db_url, connect_args=connect_args, echo=False)
    return _engine


def get_session_local():
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def init_db() -> None:
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a database session."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_upload_dir() -> None:
    """Ensure the upload directory exists."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_DIR, exist_ok=True)
