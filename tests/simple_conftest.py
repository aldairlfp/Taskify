"""
Simple test configuration
Basic fixtures for testing without complex setup
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Simple test client"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Simple async client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Simple test data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
}

TEST_TASK = {"title": "Test Task", "description": "A simple test task"}
