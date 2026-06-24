"""SQLAlchemy database models."""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON
from app.database.db import Base


class FileRecord(Base):
    """Model for uploaded file records."""
    __tablename__ = "file_records"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=False)
    analysis_type = Column(String, default="general")
    status = Column(String, default="uploaded")
    summary = Column(Text, default="")
    metadata_json = Column(JSON, default=dict)
    provider = Column(String, default="mock")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AnalysisRecord(Base):
    """Model for analysis/query records."""
    __tablename__ = "analysis_records"

    id = Column(String, primary_key=True)
    file_id = Column(String, nullable=True)
    task_type = Column(String, nullable=False)
    question = Column(Text, default="")
    answer = Column(Text, default="")
    provider = Column(String, default="mock")
    safety_status = Column(String, default="passed")
    confidence_score = Column(Float, default=0.0)
    hallucination_risk = Column(String, default="low")
    faithfulness_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    result_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SettingsRecord(Base):
    """Model for persisting user settings."""
    __tablename__ = "settings_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    default_provider = Column(String, default="mock")
    default_model = Column(String, default="gpt-4o-mini")
    vision_model = Column(String, default="gpt-4o")
    chunk_size = Column(Integer, default=512)
    similarity_threshold = Column(Float, default=0.7)
    mock_mode = Column(Integer, default=1)  # 1 = true, 0 = false
    storage_backend = Column(String, default="local")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
