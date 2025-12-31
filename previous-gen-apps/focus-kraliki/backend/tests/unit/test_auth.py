"""
Authentication Tests - Ed25519 JWT + Token Revocation
Target Coverage: 90%
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.ed25519_auth import ed25519_auth
from app.core.security_v2 import get_password_hash, verify_password
from app.models.user import User


class TestRegistration:
    """Test user registration with Ed25519 JWT."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client: AsyncClient, db: Session):
        """Test successful user registration."""
        response = await async_client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "name": "New User"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Check user data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["firstName"] == "New"

        # Check tokens exist
        assert "token" in data
        assert "refreshToken" in data

        # Verify tokens are valid Ed25519 JWT
        access_payload = ed25519_auth.verify_token(data["token"], "access")
        assert access_payload["sub"] == data["user"]["id"]
        assert access_payload["type"] == "access"

        refresh_payload = ed25519_auth.verify_token(data["refreshToken"], "refresh")
        assert refresh_payload["sub"] == data["user"]["id"]
        assert refresh_payload["type"] == "refresh"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient, test_user: User):
        """Test registration with existing email fails."""
        response = await async_client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "password": "SecurePass123!",
                "name": "Duplicate User"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Test registration with invalid email format fails."""
        response = await async_client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass123!",
                "name": "Invalid Email"
            }
        )

        assert response.status_code == 422


class TestLogin:
    """Test user login with Ed25519 JWT."""

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_user: User):
        """Test successful login with valid credentials."""
        response = await async_client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Check user data
        assert data["user"]["id"] == test_user.id
        assert data["user"]["email"] == test_user.email

        # Check tokens
        assert "token" in data
        assert "refreshToken" in data

        # Verify Ed25519 tokens
        access_payload = ed25519_auth.verify_token(data["token"], "access")
        assert access_payload["sub"] == test_user.id

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient, test_user: User):
        """Test login with wrong password fails."""
        response = await async_client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent email fails."""
        response = await async_client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword"
            }
        )

        assert response.status_code == 401


class TestTokenRefresh:
    """Test refresh token endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, async_client: AsyncClient, test_user: User):
        """Test successful token refresh."""
        # Create refresh token
        refresh_token = ed25519_auth.create_refresh_token(data={"sub": test_user.id})

        response = await async_client.post(
            "/auth/refresh",
            params={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()

        # Check new access token
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify new token is valid
        payload = ed25519_auth.verify_token(data["access_token"], "access")
        assert payload["sub"] == test_user.id

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self, async_client: AsyncClient, auth_token: str):
        """Test refresh fails when using access token instead of refresh token."""
        response = await async_client.post(
            "/auth/refresh",
            params={"refresh_token": auth_token}
        )

        # Should fail because access token has wrong type
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, async_client: AsyncClient):
        """Test refresh with invalid token fails."""
        response = await async_client.post(
            "/auth/refresh",
            params={"refresh_token": "invalid.token.here"}
        )

        assert response.status_code == 401


class TestAuthenticatedEndpoints:
    """Test authenticated endpoint access."""

    @pytest.mark.asyncio
    async def test_get_me_success(self, async_client: AsyncClient, auth_headers: dict, test_user: User):
        """Test /auth/me with valid token."""
        response = await async_client.get(
            "/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, async_client: AsyncClient):
        """Test /auth/me without token fails."""
        response = await async_client.get("/auth/me")

        assert response.status_code == 401  # No credentials provided (Unauthorized)

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, async_client: AsyncClient):
        """Test /auth/me with invalid token fails."""
        response = await async_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401


class TestPasswordChange:
    """Test password change with token revocation."""

    @pytest.mark.asyncio
    async def test_change_password_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test successful password change."""
        response = await async_client.post(
            "/auth/change-password",
            params={
                "current_password": "testpassword123",
                "new_password": "NewSecurePass456!"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify password was changed in database
        db.refresh(test_user)
        assert verify_password("NewSecurePass456!", test_user.passwordHash)

        # Old password should not work
        assert not verify_password("testpassword123", test_user.passwordHash)

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test password change with wrong current password fails."""
        response = await async_client.post(
            "/auth/change-password",
            params={
                "current_password": "wrongpassword",
                "new_password": "NewSecurePass456!"
            },
            headers=auth_headers
        )

        assert response.status_code == 401


class TestEd25519JWT:
    """Test Ed25519 JWT implementation."""

    def test_create_access_token(self):
        """Test Ed25519 access token creation."""
        token = ed25519_auth.create_access_token(data={"sub": "user123"})

        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long

        # Verify token
        payload = ed25519_auth.verify_token(token, "access")
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_refresh_token(self):
        """Test Ed25519 refresh token creation."""
        token = ed25519_auth.create_refresh_token(data={"sub": "user123"})

        assert isinstance(token, str)

        # Verify token
        payload = ed25519_auth.verify_token(token, "refresh")
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

    def test_verify_token_wrong_type(self):
        """Test verifying token with wrong expected type fails."""
        access_token = ed25519_auth.create_access_token(data={"sub": "user123"})

        with pytest.raises(Exception):  # HTTPException
            ed25519_auth.verify_token(access_token, "refresh")

    def test_verify_expired_token(self):
        """Test expired token verification fails."""
        from datetime import timedelta

        # Create token that expires immediately
        token = ed25519_auth.create_access_token(
            data={"sub": "user123"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        with pytest.raises(Exception):  # HTTPException for expired
            ed25519_auth.verify_token(token, "access")

    def test_verify_invalid_token(self):
        """Test invalid token verification fails."""
        with pytest.raises(Exception):
            ed25519_auth.verify_token("not.a.valid.token", "access")


class TestPasswordHashing:
    """Test bcrypt password hashing."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt hash prefix
        assert len(hashed) == 60  # bcrypt hash length

    def test_verify_password_correct(self):
        """Test correct password verification."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test incorrect password verification."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # Different due to salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
