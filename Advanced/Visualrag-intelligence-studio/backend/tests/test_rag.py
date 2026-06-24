"""Test PDF RAG endpoint."""
import io
from fastapi.testclient import TestClient


def test_rag_query(client: TestClient):
    """Test PDF RAG query endpoint."""
    response = client.post(
        "/api/v1/pdf-rag-query",
        json={
            "file_id": "test_file_123",
            "question": "What are the key points?",
            "provider": "mock",
            "use_rag": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "answer" in data["data"]
    assert "faithfulness_score" in data["data"]
    assert "relevance_score" in data["data"]
    assert "hallucination_risk" in data["data"]
    assert "sources" in data["data"]


def test_rag_query_without_rag(client: TestClient):
    """Test RAG query with use_rag=false."""
    response = client.post(
        "/api/v1/pdf-rag-query",
        json={
            "file_id": "test_file_123",
            "question": "Summarize this document",
            "provider": "mock",
            "use_rag": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
