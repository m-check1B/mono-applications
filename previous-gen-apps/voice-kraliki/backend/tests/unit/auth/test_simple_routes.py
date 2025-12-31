"""Test simple_routes.py user data fetching from database"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import Request

from app.auth.simple_routes import login, register
from app.models.user import User, UserRole


@pytest.fixture
def mock_request():
    """Mock FastAPI Request"""
    return MagicMock(spec=Request)


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def mock_user():
    """Mock User object"""
    user = User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.AGENT,
        is_active=True,
        password_hash="hashed_password",
    )
    return user


@pytest.mark.asyncio
async def test_login_fetches_user_from_db(mock_request, mock_db, mock_user):
    """Test that login fetches full user data from database"""
    credentials = MagicMock(email="test@example.com", password="password")

    with (
        patch("app.auth.simple_routes.real_login") as mock_real_login,
        patch("app.auth.simple_routes.get_auth_manager") as mock_get_auth_manager,
        patch("app.auth.simple_routes._extract_token_data") as mock_extract_token,
    ):
        # Setup mock responses
        mock_response = MagicMock()
        mock_response.body = (
            b'{"access_token":"test_token","refresh_token":"refresh","expires_in":3600}'
        )
        mock_real_login.return_value = mock_response
        mock_extract_token.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh",
            "expires_in": 3600,
        }

        # Setup auth manager
        mock_auth = MagicMock()
        mock_auth.verify_token.return_value = {
            "sub": "1",
            "email": "test@example.com",
            "role": "AGENT",
        }
        mock_get_auth_manager.return_value = mock_auth

        # Setup database query to return user
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_execute_result

        # Call login
        result = await login(credentials, mock_request, mock_db)

        # Verify user data comes from database, not placeholder
        assert result.user is not None
        assert result.user["id"] == "1"
        assert result.user["email"] == "test@example.com"
        assert result.user["name"] == "Test User"  # From DB, not "User Name"
        assert result.user["role"] == "AGENT"

        # Verify database was queried
        mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_register_fetches_user_from_db(mock_request, mock_db, mock_user):
    """Test that register fetches full user data from database"""
    payload = MagicMock(email="test@example.com", password="password", name="New User")

    with (
        patch("app.auth.simple_routes.real_register") as mock_real_register,
        patch("app.auth.simple_routes.get_auth_manager") as mock_get_auth_manager,
        patch("app.auth.simple_routes._extract_token_data") as mock_extract_token,
    ):
        # Setup mock responses
        mock_response = MagicMock()
        mock_response.body = (
            b'{"access_token":"test_token","refresh_token":"refresh","expires_in":3600}'
        )
        mock_real_register.return_value = mock_response
        mock_extract_token.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh",
            "expires_in": 3600,
        }

        # Setup auth manager
        mock_auth = MagicMock()
        mock_auth.verify_token.return_value = {
            "sub": "1",
            "email": "test@example.com",
            "role": "AGENT",
        }
        mock_get_auth_manager.return_value = mock_auth

        # Setup database query to return user
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_execute_result

        # Call register
        result = await register(payload, mock_request, mock_db)

        # Verify user data comes from database
        assert result.user is not None
        assert result.user["id"] == "1"
        assert result.user["email"] == "test@example.com"
        assert result.user["name"] == "Test User"  # From DB, not "New User"
        assert result.user["role"] == "AGENT"

        # Verify database was queried
        mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_login_fallback_when_user_not_in_db(mock_request, mock_db):
    """Test that login uses fallback when user not found in database"""
    credentials = MagicMock(email="test@example.com", password="password")

    with (
        patch("app.auth.simple_routes.real_login") as mock_real_login,
        patch("app.auth.simple_routes.get_auth_manager") as mock_get_auth_manager,
        patch("app.auth.simple_routes._extract_token_data") as mock_extract_token,
    ):
        # Setup mock responses
        mock_response = MagicMock()
        mock_response.body = (
            b'{"access_token":"test_token","refresh_token":"refresh","expires_in":3600}'
        )
        mock_real_login.return_value = mock_response
        mock_extract_token.return_value = {
            "access_token": "test_token",
            "refresh_token": "refresh",
            "expires_in": 3600,
        }

        # Setup auth manager
        mock_auth = MagicMock()
        mock_auth.verify_token.return_value = {
            "sub": "999",
            "email": "test@example.com",
            "role": "AGENT",
        }
        mock_get_auth_manager.return_value = mock_auth

        # Setup database query to return None (user not found)
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_execute_result

        # Call login
        result = await login(credentials, mock_request, mock_db)

        # Verify fallback is used
        assert result.user is not None
        assert result.user["email"] == "test@example.com"
        assert result.user["name"] == "User"  # Fallback value
        assert result.user["role"] == "AGENT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
