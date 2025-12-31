"""
Unit tests for Google OAuth Router
Tests Google OAuth authentication flow, account linking, and token verification
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from httpx import AsyncClient

from app.models.user import User
from app.schemas.user import GoogleAuthUrlRequest, GoogleLinkRequest


@pytest.mark.unit
class TestGoogleOAuthRouter:
    """Test Google OAuth Router API endpoints"""

    async def test_get_auth_url_success(self, async_client: AsyncClient):
        """Test successful OAuth URL generation"""
        with patch("app.routers.google_oauth.settings") as mock_settings:
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"
            mock_settings.GOOGLE_OAUTH_REDIRECT_URI = "http://localhost/callback"

            response = await async_client.post(
                "/auth/google/url", json={"state": "test-state-123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "url" in data
            assert "csrfToken" in data
            assert data["url"].startswith(
                "https://accounts.google.com/o/oauth2/v2/auth?"
            )
            assert "client_id=test-client-id" in data["url"]
            assert "state=test-state-123" in data["url"]

    async def test_get_auth_url_not_configured(self, async_client: AsyncClient):
        """Test OAuth URL generation fails when not configured"""
        with patch("app.routers.google_oauth.settings") as mock_settings:
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = None

            response = await async_client.post(
                "/auth/google/url", json={"state": "test-state"}
            )

            assert response.status_code == 503
            assert "Google OAuth is not configured" in response.json()["detail"]

    async def test_get_auth_url_includes_scopes(self, async_client: AsyncClient):
        """Test OAuth URL includes required scopes"""
        with patch("app.routers.google_oauth.settings") as mock_settings:
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"
            mock_settings.GOOGLE_OAUTH_REDIRECT_URI = "http://localhost/callback"

            response = await async_client.post(
                "/auth/google/url", json={"state": "test-state"}
            )

            assert response.status_code == 200
            url = response.json()["url"]
            assert "openid" in url
            assert "email" in url
            assert "profile" in url
            assert "calendar.readonly" in url
            assert "calendar.events" in url

    async def test_link_google_account_success(
        self, async_client: AsyncClient, test_user: User, auth_headers: dict, db
    ):
        """Test successful Google account linking"""
        with (
            patch("app.routers.google_oauth.settings") as mock_settings,
            patch("app.routers.google_oauth.id_token") as mock_id_token,
            patch("app.routers.google_oauth.csrf_tokens", {"test-state": "csrf-123"}),
        ):
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"
            mock_id_token.verify_oauth2_token.return_value = {
                "email": "linked@example.com",
                "sub": "google-sub-456",
            }

            link_request = {
                "state": "test-state",
                "csrfToken": "csrf-123",
                "idToken": "google-id-token",
            }

            response = await async_client.post(
                "/auth/google/link",
                json=link_request,
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "linked successfully" in data["message"]

    async def test_link_google_account_invalid_csrf(
        self, async_client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test account linking fails with invalid CSRF token"""
        with (
            patch("app.routers.google_oauth.settings") as mock_settings,
            patch("app.routers.google_oauth.csrf_tokens", {"test-state": "csrf-123"}),
        ):
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"

            link_request = {
                "state": "test-state",
                "csrfToken": "wrong-token",
                "idToken": "google-id-token",
            }

            response = await async_client.post(
                "/auth/google/link",
                json=link_request,
                headers=auth_headers,
            )

            assert response.status_code == 400
            assert "Invalid CSRF token" in response.json()["detail"]

    async def test_link_google_account_not_configured(
        self, async_client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test account linking fails when OAuth not configured"""
        with (
            patch("app.routers.google_oauth.settings") as mock_settings,
            patch("app.routers.google_oauth.csrf_tokens", {"test-state": "csrf-123"}),
        ):
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = None

            link_request = {
                "state": "test-state",
                "csrfToken": "csrf-123",
                "idToken": "google-id-token",
            }

            response = await async_client.post(
                "/auth/google/link",
                json=link_request,
                headers=auth_headers,
            )

            assert response.status_code == 503

    async def test_unlink_google_account_success(
        self, async_client: AsyncClient, test_user: User, auth_headers: dict, db
    ):
        """Test successful Google account unlinking"""

        response = await async_client.post("/auth/google/unlink", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "unlinked successfully" in data["message"]

    async def test_unlink_google_account_unauthorized(self, async_client: AsyncClient):
        """Test unlinking account without authentication"""
        response = await async_client.post("/auth/google/unlink")

        assert response.status_code == 401

    async def test_login_with_code_not_configured(self, async_client: AsyncClient):
        """Test login fails when OAuth not configured"""
        with patch("app.routers.google_oauth.settings") as mock_settings:
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = None
            mock_settings.GOOGLE_OAUTH_CLIENT_SECRET = None

            response = await async_client.post(
                "/auth/google/login",
                params={
                    "code": "test-code",
                    "redirect_uri": "http://localhost/callback",
                },
            )

            assert response.status_code == 503
            assert "Google OAuth is not configured" in response.json()["detail"]


@pytest.mark.unit
class TestCSRFTokenManagement:
    """Test CSRF token management"""

    async def test_csrf_token_generated(self, async_client: AsyncClient):
        """Test CSRF token is generated with OAuth URL"""
        with patch("app.routers.google_oauth.settings") as mock_settings:
            mock_settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"
            mock_settings.GOOGLE_OAUTH_REDIRECT_URI = "http://localhost/callback"

            response = await async_client.post(
                "/auth/google/url", json={"state": "unique-state-123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "csrfToken" in data
            assert len(data["csrfToken"]) > 20
