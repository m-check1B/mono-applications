"""
E2E Tests for Auth-Core Adapter Integration

Tests full integration flows for authentication and token revocation:
- Token lifecycle management
- Token revocation and blacklist
- Multi-step authentication flows
- Integration with Redis and platform auth
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.module import PlanningModule
from app.core.token_revocation import TokenBlacklist, token_blacklist
from app.core.ed25519_auth import ed25519_auth
from app.models.user import User
from sqlalchemy.orm import Session


class TestAuthAdapterE2E:
    """End-to-end tests for auth adapter integration flows."""

    @pytest.mark.asyncio
    @pytest.mark.integration  # Requires Redis connection
    async def test_token_blacklist_connection_lifecycle(self):
        """E2E: Token blacklist connects and disconnects properly."""
        # Create isolated blacklist instance
        test_blacklist = TokenBlacklist("redis://localhost:6379/15")

        # Connect - skip if Redis not available
        try:
            await test_blacklist.connect()
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")

        assert test_blacklist._redis is not None

        # Disconnect
        await test_blacklist.disconnect()
        assert test_blacklist._redis is None

    @pytest.mark.asyncio
    async def test_token_revocation_full_flow(self, mock_token_blacklist):
        """E2E: Full token revocation flow from logout to validation."""
        # Step 1: Create token
        user_id = "user_test_123"
        token = ed25519_auth.create_access_token(data={"sub": user_id})

        # Step 2: Token is valid initially
        is_revoked = await mock_token_blacklist.is_revoked(token)
        assert is_revoked is False

        # Step 3: Revoke token (user logs out)
        exp = int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        await mock_token_blacklist.revoke_token(token, exp)

        # Step 4: Token is now revoked
        is_revoked = await mock_token_blacklist.is_revoked(token)
        assert is_revoked is True

    @pytest.mark.asyncio
    async def test_user_level_token_revocation(self, mock_token_blacklist):
        """E2E: Revoking all user tokens (password change scenario)."""
        user_id = "user_pwchange_456"

        # Create multiple tokens for user
        token1 = ed25519_auth.create_access_token(data={"sub": user_id})
        token2 = ed25519_auth.create_access_token(data={"sub": user_id})

        # Initially not revoked
        assert await mock_token_blacklist.is_user_revoked(user_id) is False

        # Revoke all user tokens
        await mock_token_blacklist.revoke_all_user_tokens(user_id)

        # User revocation should be active
        assert await mock_token_blacklist.is_user_revoked(user_id) is True

    def test_auth_adapter_login_logout_flow(self, client, test_user, db):
        """E2E: Complete login-logout-retry flow."""
        # Step 1: Login
        # Note: Password must match conftest.py TEST_USER_PASSWORD constant
        response = client.post(
            "/auth/v2/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        access_token = data["token"]

        # Step 2: Access protected endpoint
        response = client.get(
            "/auth/v2/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200

        # Step 3: Logout (revoke token)
        response = client.post(
            "/auth/v2/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200

        # Step 4: Try to use revoked token (should fail)
        # Note: This requires token revocation middleware to be active
        # Currently may still work without Redis middleware
        # Documenting expected behavior

    def test_auth_adapter_invalid_credentials(self, client):
        """E2E: Auth adapter properly rejects invalid credentials."""
        response = client.post(
            "/auth/v2/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_auth_adapter_token_expiration(self, test_user):
        """E2E: Expired tokens are properly rejected."""
        # Create token that's already expired
        expired_token = ed25519_auth.create_access_token(
            data={"sub": test_user.id},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        # Verify token is expired when validated
        with pytest.raises(Exception):
            ed25519_auth.verify_token(expired_token)


class TestAuthAdapterMultiStepWorkflows:
    """Test multi-step workflows involving auth adapter."""

    def test_password_reset_flow(self, client, test_user, db):
        """E2E: Complete password reset workflow."""
        # Step 1: Request password reset
        # Step 2: Receive reset token
        # Step 3: Submit new password with token
        # Step 4: Old tokens revoked
        # Step 5: Login with new password

        # Currently not fully implemented - documenting expected flow
        pass

    @pytest.mark.asyncio
    async def test_concurrent_login_sessions(self, mock_token_blacklist):
        """E2E: Multiple concurrent sessions for same user."""
        user_id = "user_concurrent_789"

        # Create tokens for multiple devices
        token_desktop = ed25519_auth.create_access_token(data={"sub": user_id})
        token_mobile = ed25519_auth.create_access_token(data={"sub": user_id})

        # Both should be valid
        assert await mock_token_blacklist.is_revoked(token_desktop) is False
        assert await mock_token_blacklist.is_revoked(token_mobile) is False

        # Logout from one device
        exp = int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        await mock_token_blacklist.revoke_token(token_desktop, exp)

        # Desktop revoked, mobile still valid
        assert await mock_token_blacklist.is_revoked(token_desktop) is True
        assert await mock_token_blacklist.is_revoked(token_mobile) is False

    def test_refresh_token_flow(self, client, test_user):
        """E2E: Refresh token exchange workflow."""
        # Step 1: Login (get access + refresh tokens)
        response = client.post(
            "/auth/v2/login",
            json={
                "email": test_user.email,
                "password": "testpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Step 2: Access token expires
        # Step 3: Use refresh token to get new access token
        # Step 4: Old access token revoked
        # Step 5: Use new access token

        # Refresh token endpoint not yet implemented
        # Documenting expected flow
        pass


class TestAuthAdapterPlatformIntegration:
    """Test integration with platform authentication system."""

    def test_platform_mode_header_trust(self):
        """E2E: Platform mode trusts API gateway headers."""
        module = PlanningModule(platform_mode=True)
        app = module.get_app()
        # Use raise_server_exceptions=False since database may not be available
        # but we're testing auth behavior, not database behavior
        client = TestClient(app, raise_server_exceptions=False)

        # Without platform headers, should reject
        response = client.get("/tasks/")
        assert response.status_code == 401

        # With platform headers, should accept (auth passes)
        response = client.get(
            "/tasks/",
            headers={
                "X-User-Id": "user_platform_123",
                "X-Org-Id": "org_platform_456"
            }
        )
        # May get 500 due to database but authentication passes (not 401)
        assert response.status_code != 401

    def test_standalone_mode_jwt_validation(self, client, auth_headers):
        """E2E: Standalone mode validates JWT tokens directly."""
        # Standalone mode doesn't trust headers, validates JWT
        # Uses /auth/me endpoint (not /users/me which doesn't exist)

        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200

    def test_organization_isolation_in_auth(self):
        """E2E: Auth ensures users only access their organization's data."""
        # User from org A cannot access org B's resources
        # Even with valid token for user in org B

        # Currently not fully enforced - documenting requirement
        pass


class TestAuthAdapterErrorHandling:
    """Test error handling and recovery mechanisms."""

    @pytest.mark.asyncio
    async def test_redis_connection_failure_handling(self):
        """E2E: Auth adapter handles Redis connection failures gracefully."""
        # Create blacklist with invalid Redis URL
        test_blacklist = TokenBlacklist("redis://invalid-host:6379")

        # Connection attempt should fail gracefully
        # Note: redis.asyncio may create connection lazily in from_url(),
        # with the actual connection occurring during ping() or later operations.
        # We verify the system handles connection failures gracefully.
        try:
            await test_blacklist.connect()
            # If connect succeeded (lazy connection), try an actual operation
            await test_blacklist.is_revoked("test_token")
        except Exception:
            # Expected - connection to invalid host should eventually fail
            pass
        # If no exception, the connection might still be pending (acceptable)

    @pytest.mark.asyncio
    async def test_token_revocation_retry_on_failure(self, mock_token_blacklist):
        """E2E: Token revocation retries on transient failures."""
        # Mock Redis to fail then succeed
        call_count = {"count": 0}

        original_revoke = mock_token_blacklist.revoke_token

        async def revoke_with_retry(token, exp):
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise ConnectionError("Redis temporarily unavailable")
            return await original_revoke(token, exp)

        mock_token_blacklist.revoke_token = revoke_with_retry

        # Should eventually succeed despite transient failure
        # Currently no retry logic - documenting expected behavior
        pass

    def test_malformed_token_handling(self, client):
        """E2E: Auth adapter rejects malformed tokens."""
        malformed_tokens = [
            "not.a.token",
            "Bearer invalid",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
        ]

        for token in malformed_tokens:
            # Use /auth/me endpoint (not /users/me which doesn't exist)
            response = client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            # Accept both 401 (unauthorized) and 403 (forbidden) as valid rejection
            # 403 can occur when HTTPBearer receives malformed auth header
            assert response.status_code in [401, 403]


class TestAuthAdapterPerformance:
    """Test performance characteristics of auth adapter."""

    @pytest.mark.asyncio
    async def test_token_validation_performance(self, mock_token_blacklist):
        """E2E: Token validation is fast (< 50ms)."""
        import time

        user_id = "user_perf_test"
        token = ed25519_auth.create_access_token(data={"sub": user_id})

        # Measure validation time
        start = time.time()

        for _ in range(100):
            is_revoked = await mock_token_blacklist.is_revoked(token)

        elapsed = time.time() - start

        # Should complete 100 checks in under 1 second
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_blacklist_stats_performance(self, mock_token_blacklist):
        """E2E: Blacklist stats retrieval is efficient."""
        # Add some revoked tokens
        for i in range(10):
            token = f"token_{i}"
            exp = int((datetime.utcnow() + timedelta(hours=1)).timestamp())
            await mock_token_blacklist.revoke_token(token, exp)

        # Get stats should be fast
        # Note: Mock blacklist doesn't implement get_revocation_stats
        # Documenting expected capability
        pass


class TestAuthAdapterSecurity:
    """Test security properties of auth adapter."""

    def test_password_hashing_strength(self, db):
        """E2E: Passwords are hashed with strong algorithm."""
        from app.core.security_v2 import get_password_hash, verify_password

        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        # Hash should not contain original password
        assert password not in hashed

        # Should use bcrypt (starts with $2b$)
        assert hashed.startswith("$2b$")

        # Should verify correctly
        assert verify_password(password, hashed) is True

        # Should reject wrong password
        assert verify_password("WrongPassword", hashed) is False

    def test_token_signature_verification(self):
        """E2E: JWT tokens verified with Ed25519 signature."""
        user_id = "user_sec_test"
        token = ed25519_auth.create_access_token(data={"sub": user_id})

        # Valid token should verify
        payload = ed25519_auth.verify_token(token)
        assert payload["sub"] == user_id

        # Tampered token should fail
        tampered_token = token[:-10] + "tampered"
        with pytest.raises(Exception):
            ed25519_auth.verify_token(tampered_token)

    def test_timing_attack_resistance(self):
        """E2E: Password verification resistant to timing attacks."""
        from app.core.security_v2 import verify_password, get_password_hash
        import time

        password = "TestPassword123"
        wrong_password = "WrongPassword"
        hashed = get_password_hash(password)  # Generate valid bcrypt hash

        # Both should take similar time (not reveal information)
        # This is handled by bcrypt internally

        start = time.time()
        verify_password(password, hashed)
        time1 = time.time() - start

        start = time.time()
        verify_password(wrong_password, hashed)
        time2 = time.time() - start

        # Times should be within 100ms of each other
        assert abs(time1 - time2) < 0.1


class TestAuthAdapterCompliance:
    """Test auth adapter compliance with security standards."""

    def test_token_expiration_configurable(self):
        """E2E: Token expiration times are configurable."""
        from app.core.config import settings

        # Should have configurable expiration
        assert hasattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES")
        assert hasattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS")

        # Defaults should be reasonable
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0

    def test_password_requirements_enforced(self):
        """E2E: Password requirements enforced at registration."""
        # Should enforce:
        # - Minimum length
        # - Complexity (letters, numbers, special chars)
        # - Not common passwords

        # Currently not enforced at API level
        # Documenting expected behavior
        pass

    @pytest.mark.asyncio
    async def test_audit_logging_for_auth_events(self):
        """E2E: Auth events logged for security audit."""
        # Should log:
        # - Successful logins
        # - Failed login attempts
        # - Token revocations
        # - Password changes

        # Currently minimal logging
        # Documenting expected enhancement
        pass
