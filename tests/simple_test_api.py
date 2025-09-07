"""
Simple API Tests
Basic tests for main API functionality
"""

import pytest
from fastapi.testclient import TestClient


def test_app_starts(client: TestClient):
    """Test that the app starts and documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_api_documentation(client: TestClient):
    """Test API documentation endpoints"""
    # Test Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200

    # Test ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200


def test_nonexistent_endpoint(client: TestClient):
    """Test accessing non-existent endpoint returns 404"""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_health_check_or_root(client: TestClient):
    """Test root endpoint (if it exists)"""
    response = client.get("/")
    # Accept either 200 (if root exists) or 404 (if no root endpoint)
    assert response.status_code in [200, 404]
