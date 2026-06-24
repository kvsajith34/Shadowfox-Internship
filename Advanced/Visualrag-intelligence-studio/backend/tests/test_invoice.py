"""Test invoice extraction endpoint."""
import io
from fastapi.testclient import TestClient


def test_extract_invoice(client: TestClient, sample_pdf: bytes):
    """Test invoice extraction endpoint."""
    response = client.post(
        "/api/v1/extract-invoice",
        files={"file": ("invoice.pdf", io.BytesIO(sample_pdf), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "vendor_name" in data["data"]
    assert "invoice_number" in data["data"]
    assert "total_amount" in data["data"]
    assert "line_items" in data["data"]
    assert "confidence_score" in data["data"]


def test_extract_invoice_alias(client: TestClient, sample_pdf: bytes):
    """Test the unversioned invoice extraction alias."""
    response = client.post(
        "/extract-invoice",
        files={"file": ("invoice.pdf", io.BytesIO(sample_pdf), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
