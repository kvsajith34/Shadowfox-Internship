"""Test visual chat endpoint."""
from fastapi.testclient import TestClient


def test_visual_chat(client: TestClient):
    """Test visual chat endpoint."""
    response = client.post(
        "/api/v1/visual-chat",
        json={
            "message": "What is shown in this image?",
            "provider": "mock",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "answer" in data["data"]
    assert "confidence_score" in data["data"]
    assert "hallucination_risk" in data["data"]
    assert data["data"]["hallucination_risk"] in ["low", "medium", "high"]


def test_visual_chat_with_history(client: TestClient):
    """Test visual chat with conversation history."""
    response = client.post(
        "/api/v1/visual-chat",
        json={
            "message": "Tell me more",
            "provider": "mock",
            "history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_visual_chat_alias(client: TestClient):
    """Test the unversioned visual chat alias."""
    response = client.post(
        "/visual-chat",
        json={
            "message": "Describe this image",
            "provider": "mock",
        },
    )
    assert response.status_code == 200
