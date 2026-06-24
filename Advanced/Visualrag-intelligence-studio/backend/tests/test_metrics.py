"""Test metrics endpoint."""
from fastapi.testclient import TestClient


def test_get_metrics(client: TestClient):
    """Test metrics endpoint."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "totalFiles" in data["data"]
    assert "queriesHandled" in data["data"]
    assert "avgFaithfulness" in data["data"]
    assert "providerStatus" in data["data"]
    assert "evaluationTrend" in data["data"]
    assert "ragPerformance" in data["data"]
    assert "safetyAudit" in data["data"]
    assert "mock" in data["data"]["providerStatus"]


def test_metrics_alias(client: TestClient):
    """Test the unversioned metrics alias."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
