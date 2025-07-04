"""
Basic tests for the FastAPI application foundation.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns basic API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Collaborative PoC" in data["message"]
    assert data["docs"] == "/docs"
    assert data["health"] == "/healthcheck"





def test_chat_endpoint_with_valid_request():
    """Test the chat endpoint with a valid request."""
    chat_request = {
        "user_id": "test-user-123",
        "message": "I'm feeling overwhelmed today."
    }
    response = client.post("/chat/", json=chat_request)
    assert response.status_code == 200
    data = response.json()
    assert "persona_response" in data
    assert len(data["persona_response"]) > 0
    # Note: response_id and timestamp removed per backend context specs


def test_chat_endpoint_with_invalid_request():
    """Test the chat endpoint with invalid request data."""
    invalid_request = {
        "user_id": "",  # Empty user_id should fail validation
        "message": ""   # Empty message should fail validation
    }
    response = client.post("/chat/", json=invalid_request)
    assert response.status_code == 422
    data = response.json()
    assert data["type"] == "https://collaborative.solutions/errors/validation-error"
    assert data["title"] == "Validation Error"


def test_memory_endpoint():
    """Test the memory retrieval endpoint."""
    user_id = "test-user-123"
    response = client.get(f"/memory/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert "user_name" in data
    assert "sage" in data
    assert "reflections" in data["sage"]
    assert "emotions" in data["sage"]


def test_healthcheck_endpoint():
    """Test the health check endpoint as POST."""
    response = client.post("/healthcheck")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "services" in data


def test_nonexistent_endpoint():
    """Test accessing a non-existent endpoint returns proper error format."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert data["status"] == 404 