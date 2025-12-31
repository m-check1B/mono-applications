"""
Speak by Kraliki - Authentication Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_company(client: AsyncClient):
    """Test company registration."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "newuser@newcompany.com",
            "password": "securepass123",
            "first_name": "New",
            "last_name": "User",
            "company_name": "New Company Inc",
        }
    )
    assert response.status_code == 200  # FastAPI default for POST success
    data = response.json()
    assert data["email"] == "newuser@newcompany.com"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test registration with existing email fails."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "admin@test.com",  # Same as test_user
            "password": "anotherpass123",
            "first_name": "Another",
            "last_name": "User",
            "company_name": "Another Company",
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "testpass123",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with wrong password."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "wrongpassword",
        }
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "nobody@nowhere.com",
            "password": "anypassword",
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user, auth_headers):
    """Test getting current user info."""
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["first_name"] == "Test"
    assert data["role"] == "owner"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected endpoint without auth."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    """Test accessing with invalid token."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user):
    """Test token refresh."""
    # First login to get tokens
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "testpass123",
        }
    )
    tokens = login_response.json()

    # Refresh the token
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
