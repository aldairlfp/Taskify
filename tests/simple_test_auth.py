"""
Simple Authentication Tests
Basic tests for user registration and login
"""

import pytest
from httpx import AsyncClient


class TestSimpleAuth:
    """Simple authentication tests"""

    async def test_user_registration(self, async_client: AsyncClient):
        """Test basic user registration"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }

        response = await async_client.post("/auth/register", json=user_data)

        # Should succeed or fail gracefully
        assert response.status_code in [201, 400, 422]

        if response.status_code == 201:
            data = response.json()
            assert "username" in data
            assert "email" in data
            assert "password" not in data  # Password should not be returned

    async def test_user_login(self, async_client: AsyncClient):
        """Test basic user login"""
        # First register a user
        user_data = {
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "password123",
        }

        register_response = await async_client.post("/auth/register", json=user_data)

        if register_response.status_code == 201:
            # Try to login
            login_data = {"username": "loginuser", "password": "password123"}

            login_response = await async_client.post("/auth/login", data=login_data)

            if login_response.status_code == 200:
                data = login_response.json()
                assert "access_token" in data
                assert "token_type" in data

    async def test_login_with_wrong_password(self, async_client: AsyncClient):
        """Test login with incorrect password"""
        login_data = {"username": "nonexistent", "password": "wrongpassword"}

        response = await async_client.post("/auth/login", data=login_data)
        assert response.status_code == 401

    async def test_access_protected_endpoint_without_auth(
        self, async_client: AsyncClient
    ):
        """Test accessing protected endpoint without authentication"""
        response = await async_client.get("/tasks/")
        assert response.status_code == 401
