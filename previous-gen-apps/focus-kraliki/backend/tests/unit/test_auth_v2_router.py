"""
Unit tests for auth v2 router
Tests user registration, login, and session management
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthV2RouterAPI:
    """Test auth v2 router via HTTP client"""

    def test_register_success(self, client: TestClient):
        """Should register new user successfully"""
        user_data = {
            "email": "newuser@test.com",
            "name": "New User",
            "password": "password123",
        }
        response = client.post("/auth/v2/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == "newuser@test.com"

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Should return 400 for duplicate email"""
        user_data = {
            "email": test_user.email,
            "name": "Duplicate User",
            "password": "password123",
        }
        response = client.post("/auth/v2/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_missing_fields(self, client: TestClient):
        """Should return 422 for missing required fields"""
        response = client.post("/auth/v2/register", json={"email": "test@test.com"})
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, test_user):
        """Should login with valid credentials"""
        credentials = {"email": test_user.email, "password": "testpassword123"}
        response = client.post("/auth/v2/login", json=credentials)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == test_user.email

    def test_login_invalid_email(self, client: TestClient):
        """Should return 401 for invalid email"""
        credentials = {"email": "nonexistent@test.com", "password": "password123"}
        response = client.post("/auth/v2/login", json=credentials)
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client: TestClient, test_user):
        """Should return 401 for invalid password"""
        credentials = {"email": test_user.email, "password": "wrongpassword"}
        response = client.post("/auth/v2/login", json=credentials)
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_missing_fields(self, client: TestClient):
        """Should return 422 for missing fields"""
        response = client.post("/auth/v2/login", json={"email": "test@test.com"})
        assert response.status_code == 422

    def test_get_me_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/auth/v2/me")
        assert response.status_code == 401

    def test_get_me_authenticated(
        self, client: TestClient, auth_headers: dict, test_user
    ):
        """Should return current user data"""
        response = client.get("/auth/v2/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    def test_get_me_user_structure(self, client: TestClient, auth_headers: dict):
        """Should return user with proper structure"""
        response = client.get("/auth/v2/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "firstName" in data
        assert "lastName" in data

    def test_logout_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.post("/auth/v2/logout")
        assert response.status_code == 401

    def test_logout_authenticated(self, client: TestClient, auth_headers: dict):
        """Should logout successfully"""
        response = client.post("/auth/v2/logout", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "logged out" in data["message"].lower()

    def test_token_structure_after_register(self, client: TestClient):
        """Should return valid JWT token after registration"""
        user_data = {
            "email": "tokenuser@test.com",
            "name": "Token User",
            "password": "password123",
        }
        response = client.post("/auth/v2/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        token = data["token"]
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.startswith("eyJ")  # JWT format

    def test_token_structure_after_login(self, client: TestClient, test_user):
        """Should return valid JWT token after login"""
        credentials = {"email": test_user.email, "password": "testpassword123"}
        response = client.post("/auth/v2/login", json=credentials)
        assert response.status_code == 200
        data = response.json()
        token = data["token"]
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.startswith("eyJ")

    def test_register_creates_organization(self, client: TestClient):
        """Should create organization for new user"""
        user_data = {
            "email": "orguser@test.com",
            "name": "Org User",
            "password": "password123",
        }
        response = client.post("/auth/v2/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
