"""Tests for main application."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint.

    Args:
        client: Test client
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_root(client: TestClient) -> None:
    """Test API root endpoint.

    Args:
        client: Test client
    """
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Welcome to The AI Exchange" in data["message"]
