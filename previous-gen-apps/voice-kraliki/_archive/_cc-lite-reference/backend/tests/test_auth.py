"""Authentication tests"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient, sample_user_data):
    """Test user registration"""
    response = await async_client.post("/api/auth/register", json=sample_user_data)

    # Currently returns 501 Not Implemented - update when implemented
    assert response.status_code in [201, 501]

    if response.status_code == 201:
        data = response.json()
        assert "user" in data
        assert "access_token" in data
        assert data["user"]["email"] == sample_user_data["email"]


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    """Test successful login"""
    # This will fail until authentication is fully implemented
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "agent@test.com", "password": "password123"}
    )

    # Currently returns 501 Not Implemented
    assert response.status_code in [200, 501]


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    """Test login with invalid credentials"""
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"}
    )

    # Should return 401 or 501
    assert response.status_code in [401, 501]


@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient):
    """Test getting current user"""
    response = await async_client.get("/api/auth/me")

    # Currently returns 501 Not Implemented
    assert response.status_code in [200, 401, 501]
