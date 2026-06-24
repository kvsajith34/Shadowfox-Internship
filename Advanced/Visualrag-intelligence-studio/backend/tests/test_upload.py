"""Test upload endpoint."""
import io
from fastapi.testclient import TestClient


def test_upload_text_file(client: TestClient, sample_text: bytes):
    """Test uploading a text file."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.txt", io.BytesIO(sample_text), "text/plain")},
        data={"analysisType": "general"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["file_id"].startswith("file_")
    assert data["data"]["filename"] == "test.txt"
    assert data["data"]["file_type"] == "text"
    assert data["data"]["status"] == "uploaded"


def test_upload_pdf_file(client: TestClient, sample_pdf: bytes):
    """Test uploading a PDF file."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.pdf", io.BytesIO(sample_pdf), "application/pdf")},
        data={"analysisType": "rag"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["file_type"] == "pdf"


def test_upload_invalid_file(client: TestClient):
    """Test uploading an invalid file type."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.exe", io.BytesIO(b"invalid"), "application/octet-stream")},
        data={"analysisType": "general"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "not allowed" in data["message"].lower()


def test_upload_alias(client: TestClient, sample_text: bytes):
    """Test the unversioned upload alias."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", io.BytesIO(sample_text), "text/plain")},
        data={"analysisType": "general"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
