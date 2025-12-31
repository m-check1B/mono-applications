"""
Tests for JWT Authentication module.

Tests cover:
- Token verification
- Token revocation checks
- User authentication
- Token creation
- Role and permission checks
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4

from fastapi import HTTPException

from app.auth.jwt_auth import (
    JWTAuthManager,
    get_jwt_auth_manager,
    require_permissions,
    require_role,
)
from app.models.user import User, UserRole, Permission


@pytest.fixture
def mock_auth_manager():
    """Create a mock ed25519 auth manager."""
    mock = MagicMock()
    mock.verify_token.return_value = {
        "sub": str(uuid4()),
        "email": f"test-{uuid4()}@example.com",
        "role": "AGENT",
        "jti": "test-jti-123",
        "iat": datetime.now(timezone.utc).timestamp(),
    }
    mock.hash_password.return_value = "hashed_password"
    mock.verify_password.return_value = True
    mock.create_access_token.return_value = "access_token_123"
    mock.create_refresh_token.return_value = "refresh_token_123"
    return mock


@pytest.fixture
def mock_revocation_service():
    """Create a mock revocation service."""
    mock = MagicMock()
    mock.is_token_revoked.return_value = False
    mock.is_token_revoked_for_user.return_value = False
    return mock


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock()
    return db


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = MagicMock(spec=User)
    user.id = str(uuid4())
    user.email = f"test-{uuid4()}@example.com"
    user.full_name = "Test User"
    user.password_hash = "hashed_password"
    user.role = UserRole.AGENT
    user.organization = None
    user.is_active = True
    user.is_verified = True
    user.permissions = []
    user.last_login_at = None
    return user


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user."""
    user = MagicMock(spec=User)
    user.id = str(uuid4())
    user.email = f"admin-{uuid4()}@example.com"
    user.full_name = "Admin User"
    user.role = UserRole.ADMIN
    user.is_active = True
    user.is_verified = True
    user.permissions = [p.value for p in Permission]
    return user


class TestJWTAuthManager:
    """Tests for JWTAuthManager class."""

    def test_verify_token_valid(self, mock_auth_manager, mock_revocation_service):
        """Test token verification with valid token."""
        with (
            patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager),
            patch("app.auth.jwt_auth.get_revocation_service", return_value=mock_revocation_service),
        ):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.verify_token("valid_token")

            assert result is not None
            assert "sub" in result
            assert "email" in result

    def test_verify_token_invalid(self, mock_revocation_service):
        """Test token verification with invalid token."""
        mock_auth = MagicMock()
        mock_auth.verify_token.return_value = None

        with patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.verify_token("invalid_token")

            assert result is None

    def test_verify_token_revoked(self, mock_auth_manager):
        """Test token verification with revoked token."""
        mock_revocation = MagicMock()
        mock_revocation.is_token_revoked.return_value = True

        with (
            patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager),
            patch("app.auth.jwt_auth.get_revocation_service", return_value=mock_revocation),
        ):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.verify_token("revoked_token")

            assert result is None

    def test_verify_token_user_revoked(self, mock_auth_manager):
        """Test token verification when user's tokens are revoked."""
        mock_revocation = MagicMock()
        mock_revocation.is_token_revoked.return_value = False
        mock_revocation.is_token_revoked_for_user.return_value = True

        with (
            patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager),
            patch("app.auth.jwt_auth.get_revocation_service", return_value=mock_revocation),
        ):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.verify_token("old_token")

            assert result is None

    def test_hash_password(self, mock_auth_manager, mock_revocation_service):
        """Test password hashing."""
        with patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.hash_password("test_password")

            assert result == "hashed_password"
            mock_auth_manager.hash_password.assert_called_once_with("test_password")


class TestGetUserFromToken:
    """Tests for get_user_from_token method."""

    def test_get_user_from_valid_token(
        self, mock_auth_manager, mock_revocation_service, mock_db, mock_user
    ):
        """Test getting user from valid token."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        with (
            patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager),
            patch("app.auth.jwt_auth.get_revocation_service", return_value=mock_revocation_service),
        ):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.get_user_from_token("valid_token", mock_db)

            assert result == mock_user

    def test_get_user_from_invalid_token(self, mock_revocation_service, mock_db):
        """Test getting user from invalid token."""
        mock_auth = MagicMock()
        mock_auth.verify_token.return_value = None

        with patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.get_user_from_token("invalid_token", mock_db)

            assert result is None

    def test_get_user_not_found(self, mock_auth_manager, mock_revocation_service, mock_db):
        """Test getting user that doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with (
            patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager),
            patch("app.auth.jwt_auth.get_revocation_service", return_value=mock_revocation_service),
        ):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.get_user_from_token("valid_token", mock_db)

            assert result is None


class TestAuthenticateUser:
    """Tests for authenticate_user method."""

    def test_authenticate_user_success(
        self, mock_auth_manager, mock_revocation_service, mock_db, mock_user
    ):
        """Test successful user authentication."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        with patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.authenticate_user("test@example.com", "password", mock_db)

            assert result == mock_user
            mock_db.commit.assert_called_once()

    def test_authenticate_user_not_found(self, mock_auth_manager, mock_db):
        """Test authentication with non-existent user."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.authenticate_user("nonexistent@example.com", "password", mock_db)

            assert result is None

    def test_authenticate_user_wrong_password(self, mock_auth_manager, mock_db, mock_user):
        """Test authentication with wrong password."""
        mock_auth_manager.verify_password.return_value = False
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        with patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.authenticate_user("test@example.com", "wrong_password", mock_db)

            assert result is None


class TestCreateUserTokens:
    """Tests for create_user_tokens method."""

    def test_create_user_tokens_structure(self, mock_auth_manager, mock_user):
        """Test token creation returns correct structure."""
        with patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager):
            jwt_manager = JWTAuthManager()
            result = jwt_manager.create_user_tokens(mock_user)

            assert "access_token" in result
            assert "refresh_token" in result
            assert "token_type" in result
            assert "expires_in" in result
            assert result["token_type"] == "bearer"

    def test_create_user_tokens_calls_auth_manager(self, mock_auth_manager, mock_user):
        """Test that token creation calls auth manager correctly."""
        with patch("app.auth.jwt_auth.get_auth_manager", return_value=mock_auth_manager):
            jwt_manager = JWTAuthManager()
            jwt_manager.create_user_tokens(mock_user)

            mock_auth_manager.create_access_token.assert_called_once()
            mock_auth_manager.create_refresh_token.assert_called_once()


class TestGetJWTAuthManager:
    """Tests for get_jwt_auth_manager singleton."""

    def test_get_jwt_auth_manager_returns_instance(self):
        """Test that get_jwt_auth_manager returns a JWTAuthManager instance."""
        with patch("app.auth.jwt_auth.get_auth_manager"):
            result = get_jwt_auth_manager()
            assert result is not None

    def test_get_jwt_auth_manager_returns_same_instance(self):
        """Test that get_jwt_auth_manager returns singleton."""
        with patch("app.auth.jwt_auth.get_auth_manager"):
            result1 = get_jwt_auth_manager()
            result2 = get_jwt_auth_manager()
            assert result1 is result2


class TestRequirePermissions:
    """Tests for require_permissions decorator."""

    @pytest.mark.asyncio
    async def test_require_permissions_success(self, mock_admin_user):
        """Test that user with required permissions passes."""
        checker = require_permissions([Permission.CAMPAIGN_READ])

        # The checker is a dependency that should not raise
        # In real usage, it would be called via FastAPI's Depends
        # Here we test the logic directly
        result = await checker(current_user=mock_admin_user)
        assert result == mock_admin_user

    @pytest.mark.asyncio
    async def test_require_permissions_missing_permission(self, mock_user):
        """Test that user without required permissions fails."""
        mock_user.permissions = []
        checker = require_permissions([Permission.CAMPAIGN_WRITE])

        with pytest.raises(HTTPException) as exc_info:
            await checker(current_user=mock_user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_permissions_multiple(self, mock_admin_user):
        """Test requiring multiple permissions."""
        checker = require_permissions([Permission.CAMPAIGN_READ, Permission.ANALYTICS_READ])

        result = await checker(current_user=mock_admin_user)
        assert result == mock_admin_user


class TestRequireRole:
    """Tests for require_role decorator."""

    @pytest.mark.asyncio
    async def test_require_role_success(self, mock_admin_user):
        """Test that user with required role passes."""
        checker = require_role([UserRole.ADMIN])

        result = await checker(current_user=mock_admin_user)
        assert result == mock_admin_user

    @pytest.mark.asyncio
    async def test_require_role_wrong_role(self, mock_user):
        """Test that user without required role fails."""
        checker = require_role([UserRole.ADMIN])

        with pytest.raises(HTTPException) as exc_info:
            await checker(current_user=mock_user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_role_multiple_allowed(self, mock_user):
        """Test that user with one of allowed roles passes."""
        checker = require_role([UserRole.AGENT, UserRole.ADMIN])

        result = await checker(current_user=mock_user)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_require_role_string_input(self, mock_admin_user):
        """Test require_role with string role input."""
        checker = require_role(["ADMIN"])

        result = await checker(current_user=mock_admin_user)
        assert result == mock_admin_user


class TestCommonRoleDependencies:
    """Tests for common role dependencies."""

    @pytest.mark.asyncio
    async def test_require_admin_with_admin(self, mock_admin_user):
        """Test require_admin with admin user."""
        from app.auth.jwt_auth import require_admin

        result = await require_admin(current_user=mock_admin_user)
        assert result == mock_admin_user

    @pytest.mark.asyncio
    async def test_require_admin_with_agent_fails(self, mock_user):
        """Test require_admin fails with agent user."""
        from app.auth.jwt_auth import require_admin

        with pytest.raises(HTTPException):
            await require_admin(current_user=mock_user)

    @pytest.mark.asyncio
    async def test_require_agent_with_agent(self, mock_user):
        """Test require_agent with agent user."""
        from app.auth.jwt_auth import require_agent

        result = await require_agent(current_user=mock_user)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_require_agent_with_admin(self, mock_admin_user):
        """Test require_agent also works with admin."""
        from app.auth.jwt_auth import require_agent

        result = await require_agent(current_user=mock_admin_user)
        assert result == mock_admin_user
