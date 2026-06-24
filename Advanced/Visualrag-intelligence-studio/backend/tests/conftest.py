"""Test fixtures and configuration.

Environment variables MUST be set before importing the app,
because app.core.config.Settings reads them at module load time.
"""
import os
import sys

# ─── Ensure backend directory is importable ──────────────────
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# ─── Set test environment BEFORE any app imports ─────────────
os.environ["MOCK_MODE"] = "true"
os.environ["DEFAULT_PROVIDER"] = "mock"
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_visualrag.db"
os.environ["UPLOAD_DIR"] = "./test_uploads"
os.environ["CHROMA_DIR"] = "./test_chroma_db"
os.environ["CORS_ORIGINS"] = '["http://localhost:5173"]'
os.environ["STORAGE_BACKEND"] = "local"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base, get_db
from main import app


# ─── Test database ───────────────────────────────────────────
TEST_DB_URL = "sqlite:///./test_visualrag.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency globally
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    """Cleanup test artifacts after entire test session."""
    yield
    for path in ["test_visualrag.db", "test_visualrag.db-journal"]:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_pdf():
    """Create a minimal PDF file for testing."""
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Test Invoice) Tj ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
310
%%EOF"""
    return pdf_content


@pytest.fixture
def sample_text():
    """Sample text content for testing."""
    return b"This is a test document for VisualRAG Intelligence Studio. It contains sample text for testing purposes."


@pytest.fixture
def sample_csv():
    """Sample CSV content for testing."""
    return b"Name,Amount,Date\nInvoice A,1500.00,2025-01-15\nInvoice B,2300.50,2025-01-16\nInvoice C,890.00,2025-01-17"
