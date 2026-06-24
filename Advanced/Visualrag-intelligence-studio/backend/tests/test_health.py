"""Test health endpoint."""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test the health check endpoint returns expected structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "data" in data
    assert "mock_mode" in data
    assert "provider" in data
    assert "timestamp" in data
    assert data["data"]["status"] == "healthy"
    assert data["data"]["mock_mode"] is True


def test_health_alias(client: TestClient):
    """Test the unversioned health alias."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
