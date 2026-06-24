#!/usr/bin/env python3
"""Seed the database with demo data for testing and presentations."""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("MOCK_MODE", "true")
os.environ.setdefault("DEFAULT_PROVIDER", "mock")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("DATABASE_URL", "sqlite:///./visualrag.db")

from app.database.db import init_db, get_session_local
from app.database.models import FileRecord, AnalysisRecord, SettingsRecord
from app.database.crud import create_file_record, create_analysis_record
from datetime import datetime, timezone


def seed():
    """Seed database with demo data."""
    init_db()
    SessionLocal = get_session_local()
    db = SessionLocal()

    try:
        # Seed file records
        files = [
            {"id": "file_demo_001", "filename": "quarterly_report.pdf", "file_type": "pdf", "size_bytes": 245000,
             "storage_path": "demo/quarterly_report.pdf", "analysis_type": "rag", "status": "analyzed",
             "summary": "Q4 2024 financial report with revenue and growth metrics", "provider": "mock"},
            {"id": "file_demo_002", "filename": "invoice_2025_01.pdf", "file_type": "pdf", "size_bytes": 89000,
             "storage_path": "demo/invoice_2025_01.pdf", "analysis_type": "invoice", "status": "analyzed",
             "summary": "Vendor invoice for consulting services - $4,158.00", "provider": "mock"},
            {"id": "file_demo_003", "filename": "sales_chart.png", "file_type": "image", "size_bytes": 156000,
             "storage_path": "demo/sales_chart.png", "analysis_type": "chart", "status": "analyzed",
             "summary": "Bar chart showing quarterly sales trends", "provider": "mock"},
            {"id": "file_demo_004", "filename": "product_photo.jpg", "file_type": "image", "size_bytes": 320000,
             "storage_path": "demo/product_photo.jpg", "analysis_type": "visual_chat", "status": "analyzed",
             "summary": "Product photography analysis - design and features", "provider": "mock"},
            {"id": "file_demo_005", "filename": "contract_v2.pdf", "file_type": "pdf", "size_bytes": 178000,
             "storage_path": "demo/contract_v2.pdf", "analysis_type": "rag", "status": "flagged",
             "summary": "Service contract with flagged termination clause", "provider": "mock"},
        ]

        for f in files:
            existing = db.query(FileRecord).filter(FileRecord.id == f["id"]).first()
            if not existing:
                record = FileRecord(**f, metadata_json={})
                db.add(record)

        # Seed analysis records
        analyses = [
            {"id": "analysis_demo_001", "file_id": "file_demo_001", "task_type": "rag",
             "question": "Summarize key financial metrics", "answer": "Revenue grew 15% QoQ...",
             "provider": "mock", "safety_status": "passed", "confidence_score": 0.91, "hallucination_risk": "low",
             "faithfulness_score": 0.89, "relevance_score": 0.92},
            {"id": "analysis_demo_002", "file_id": "file_demo_002", "task_type": "invoice",
             "question": "extract_invoice", "answer": "$4,158.00",
             "provider": "mock", "safety_status": "passed", "confidence_score": 0.94, "hallucination_risk": "low",
             "faithfulness_score": 0.92, "relevance_score": 0.95},
            {"id": "analysis_demo_003", "file_id": "file_demo_003", "task_type": "chart",
             "question": "What trend does this chart show?", "answer": "Upward revenue trend...",
             "provider": "mock", "safety_status": "passed", "confidence_score": 0.87, "hallucination_risk": "low",
             "faithfulness_score": 0.85, "relevance_score": 0.88},
            {"id": "analysis_demo_004", "file_id": "file_demo_004", "task_type": "visual_chat",
             "question": "Describe this product", "answer": "Product features include...",
             "provider": "mock", "safety_status": "passed", "confidence_score": 0.83, "hallucination_risk": "low",
             "faithfulness_score": 0.81, "relevance_score": 0.85},
            {"id": "analysis_demo_005", "file_id": "file_demo_005", "task_type": "rag",
             "question": "What are the termination conditions?", "answer": "Unusual clause detected...",
             "provider": "mock", "safety_status": "flagged", "confidence_score": 0.72, "hallucination_risk": "medium",
             "faithfulness_score": 0.70, "relevance_score": 0.78},
        ]

        for a in analyses:
            existing = db.query(AnalysisRecord).filter(AnalysisRecord.id == a["id"]).first()
            if not existing:
                record = AnalysisRecord(**a, result_json={})
                db.add(record)

        # Seed settings
        existing_settings = db.query(SettingsRecord).first()
        if not existing_settings:
            db.add(SettingsRecord())

        db.commit()
        print(f"✅ Seeded {len(files)} file records and {len(analyses)} analysis records")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
