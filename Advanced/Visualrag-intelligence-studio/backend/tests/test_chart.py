"""Test chart analysis endpoint."""
import io
from fastapi.testclient import TestClient


def test_analyze_chart(client: TestClient):
    """Test chart analysis endpoint with a simple image."""
    # Create a minimal PNG file (1x1 pixel)
    png_header = b"\x89PNG\r\n\x1a\n"
    # Minimal valid PNG
    from PIL import Image
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/v1/analyze-chart",
        files={"file": ("chart.png", buf, "image/png")},
        data={"question": "What trend does this chart show?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "chart_type" in data["data"]
    assert "key_insights" in data["data"]
    assert "confidence_score" in data["data"]


def test_analyze_chart_without_question(client: TestClient):
    """Test chart analysis without a question."""
    from PIL import Image
    img = Image.new("RGB", (200, 100), color="green")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/v1/analyze-chart",
        files={"file": ("chart.png", buf, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
