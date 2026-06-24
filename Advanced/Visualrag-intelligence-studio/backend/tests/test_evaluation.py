"""Test evaluation endpoint."""
from fastapi.testclient import TestClient


def test_evaluate(client: TestClient):
    """Test evaluation endpoint."""
    response = client.post(
        "/api/v1/evaluate",
        json={
            "question": "What is shown in this chart?",
            "answer": "The chart shows a bar graph with quarterly revenue data showing an upward trend.",
            "evidence": ["Q1: $1.6M", "Q2: $1.9M", "Q3: $2.1M", "Q4: $2.4M"],
            "task_type": "chart",
            "provider": "mock",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "relevance_score" in data["data"]
    assert "faithfulness_score" in data["data"]
    assert "completeness_score" in data["data"]
    assert "safety_score" in data["data"]
    assert "hallucination_risk" in data["data"]
    assert data["data"]["hallucination_risk"] in ["low", "medium", "high"]


def test_evaluate_without_evidence(client: TestClient):
    """Test evaluation without evidence."""
    response = client.post(
        "/api/v1/evaluate",
        json={
            "question": "Describe the image",
            "answer": "The image contains a landscape.",
            "evidence": [],
            "task_type": "visual_chat",
            "provider": "mock",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Should still work but with lower faithfulness
    assert data["data"]["faithfulness_score"] >= 0


def test_evaluate_alias(client: TestClient):
    """Test the unversioned evaluation alias."""
    response = client.post(
        "/evaluate",
        json={
            "question": "What is the total?",
            "answer": "$4,158.00",
            "evidence": ["Subtotal: $3,850.00", "Tax: $308.00"],
            "task_type": "invoice",
            "provider": "mock",
        },
    )
    assert response.status_code == 200
