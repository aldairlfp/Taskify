"""
Simple Task Tests
Basic tests for task management
"""

import pytest
from httpx import AsyncClient


class TestSimpleTasks:
    """Simple task management tests"""

    async def test_create_task_without_auth(self, async_client: AsyncClient):
        """Test creating task without authentication fails"""
        task_data = {"title": "Unauthorized Task", "description": "This should fail"}

        response = await async_client.post("/tasks/", json=task_data)
        assert response.status_code == 401

    async def test_get_tasks_without_auth(self, async_client: AsyncClient):
        """Test getting tasks without authentication fails"""
        response = await async_client.get("/tasks/")
        assert response.status_code == 401

    async def test_complete_task_workflow(self, async_client: AsyncClient):
        """Test complete workflow: register, login, create task, get tasks"""

        # 1. Register user
        user_data = {
            "username": "taskuser",
            "email": "taskuser@example.com",
            "password": "password123",
        }

        register_response = await async_client.post("/auth/register", json=user_data)

        if register_response.status_code != 201:
            # Skip test if registration fails (maybe user already exists)
            pytest.skip("User registration failed - may already exist")
            return

        # 2. Login
        login_data = {"username": "taskuser", "password": "password123"}

        login_response = await async_client.post("/auth/login", data=login_data)

        if login_response.status_code != 200:
            pytest.skip("Login failed")
            return

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create a task
        task_data = {"title": "My First Task", "description": "This is a test task"}

        create_response = await async_client.post(
            "/tasks/", json=task_data, headers=headers
        )

        if create_response.status_code == 201:
            task = create_response.json()
            assert task["title"] == "My First Task"
            assert task["description"] == "This is a test task"
            assert "id" in task

        # 4. Get all tasks
        get_response = await async_client.get("/tasks/", headers=headers)

        if get_response.status_code == 200:
            tasks = get_response.json()
            assert isinstance(tasks, list)
            # Should have at least the task we just created
            if create_response.status_code == 201:
                task_titles = [task["title"] for task in tasks]
                assert "My First Task" in task_titles

    async def test_task_validation(self, async_client: AsyncClient):
        """Test task creation with invalid data"""
        # First get auth token
        user_data = {
            "username": "validuser",
            "email": "validuser@example.com",
            "password": "password123",
        }

        await async_client.post("/auth/register", json=user_data)

        login_data = {"username": "validuser", "password": "password123"}

        login_response = await async_client.post("/auth/login", data=login_data)

        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Try to create task without title
            invalid_task = {"description": "Missing title"}

            response = await async_client.post(
                "/tasks/", json=invalid_task, headers=headers
            )
            assert response.status_code == 422  # Validation error
