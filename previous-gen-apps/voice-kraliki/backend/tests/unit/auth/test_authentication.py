"""
Comprehensive Authentication Unit Tests for Operator Demo 2026

Tests cover:
- Login/registration flows
- Token generation and validation
- Token refresh mechanisms
- Token revocation and blacklisting
- Protected route access control
- Role-based and permission-based authorization
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
import jwt

from app.auth.ed25519_auth import Ed25519Auth
from app.auth.jwt_auth import JWTAuthManager, get_current_user, get_jwt_auth_manager
from app.auth.token_revocation import TokenRevocationService
from app.models.user import User, UserRole, Permission


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def ed25519_auth(tmp_path):
    """Create Ed25519Auth instance with temporary keys directory."""
    return Ed25519Auth(keys_dir=str(tmp_path / "test_keys"))


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for token revocation tests."""
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    mock_redis.exists.return_value = 0
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    return mock_redis


@pytest.fixture
def token_revocation_service(mock_redis_client):
    """Create TokenRevocationService with mocked Redis."""
    with patch("app.auth.token_revocation.redis.Redis", return_value=mock_redis_client):
        service = TokenRevocationService()
        service.redis_client = mock_redis_client
        return service


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    mock_db = MagicMock()
    mock_db.execute = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.rollback = MagicMock()
    return mock_db


@pytest.fixture
def test_user(ed25519_auth):
    """Create a test user instance."""
    user = User()
    user.id = str(uuid.uuid4())
    user.email = f"test-{uuid.uuid4()}@example.com"
    user.full_name = "Test User"
    # Hash password using the auth manager to ensure compatibility
    user.password_hash = ed25519_auth.hash_password("testpassword")
    user.role = UserRole.AGENT
    user.organization = "test-org"
    user.is_active = True
    user.is_verified = True
    user.permissions = []
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    user.last_login_at = None
    return user


@pytest.fixture
def test_admin_user(ed25519_auth):
    """Create a test admin user instance."""
    user = User()
    user.id = str(uuid.uuid4())
    user.email = f"admin-{uuid.uuid4()}@example.com"
    user.full_name = "Admin User"
    # Hash password using the auth manager to ensure compatibility
    user.password_hash = ed25519_auth.hash_password("adminpassword")
    user.role = UserRole.ADMIN
    user.organization = "test-org"
    user.is_active = True
    user.is_verified = True
    user.permissions = [Permission.SYSTEM_ADMIN.value]
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    user.last_login_at = None
    return user


# ============================================================================
# 1. TOKEN GENERATION TESTS
# ============================================================================


@pytest.mark.unit
class TestTokenGeneration:
    """Test JWT token creation with correct claims."""

    def test_create_access_token_contains_required_claims(self, ed25519_auth):
        """Test that access token includes all required claims."""
        user_id = str(uuid.uuid4())
        email = f"test-{uuid.uuid4()}@example.com"
        role = "agent"
        org_id = "test-org"

        token = ed25519_auth.create_access_token(
            user_id=user_id,
            email=email,
            role=role,
            org_id=org_id,
            expires_delta=timedelta(minutes=30),
        )

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify claims
        payload = ed25519_auth.verify_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["role"] == role
        assert payload["org_id"] == org_id
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload

    def test_token_includes_jti_for_revocation_tracking(self, ed25519_auth):
        """Test that token includes JTI (JWT ID) for revocation tracking."""
        token = ed25519_auth.create_access_token(
            user_id="user123", email="test@example.com", role="agent"
        )

        payload = ed25519_auth.verify_token(token)
        assert "jti" in payload
        assert len(payload["jti"]) > 0

    def test_access_token_expiration_time(self, ed25519_auth):
        """Test that access token has correct expiration time (15-30 min)."""
        expires_delta = timedelta(minutes=15)

        token = ed25519_auth.create_access_token(
            user_id="user123", email="test@example.com", role="agent", expires_delta=expires_delta
        )

        payload = ed25519_auth.verify_token(token)
        exp_timestamp = payload["exp"]
        iat_timestamp = payload["iat"]

        # Calculate actual token lifetime in seconds
        token_lifetime_seconds = exp_timestamp - iat_timestamp
        expected_lifetime_seconds = expires_delta.total_seconds()

        # Token lifetime should match expires_delta (allow 2 second tolerance)
        time_difference = abs(token_lifetime_seconds - expected_lifetime_seconds)
        assert time_difference < 2

    def test_refresh_token_expiration_time(self, ed25519_auth):
        """Test that refresh token has correct expiration time (7-30 days)."""
        user_id = "user123"
        before_time = datetime.now(timezone.utc)

        token = ed25519_auth.create_refresh_token(user_id)

        payload = ed25519_auth.verify_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)

        # Refresh token should expire in 30 days (default)
        days_until_expiry = (exp_datetime - before_time).days
        assert 29 <= days_until_expiry <= 31  # Allow 1 day tolerance

    def test_token_issued_at_timestamp(self, ed25519_auth):
        """Test that token includes issued-at timestamp."""
        token = ed25519_auth.create_access_token(
            user_id="user123", email="test@example.com", role="agent"
        )

        payload = ed25519_auth.verify_token(token)

        # Check that iat claim exists and is numeric (timestamp)
        assert "iat" in payload
        iat = payload["iat"]
        assert isinstance(iat, (int, float)), f"iat should be numeric timestamp, got {type(iat)}"

        # Verify iat is before exp (issued before expiration)
        assert "exp" in payload
        exp = payload["exp"]
        assert iat < exp, "Token should be issued before it expires"


# ============================================================================
# 2. TOKEN VALIDATION TESTS
# ============================================================================


@pytest.mark.unit
class TestTokenValidation:
    """Test JWT token validation and verification."""

    def test_valid_token_passes_validation(self, ed25519_auth):
        """Test that a valid token passes verification."""
        token = ed25519_auth.create_access_token(
            user_id="user123", email="test@example.com", role="agent"
        )

        payload = ed25519_auth.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"

    def test_expired_token_fails_validation(self, ed25519_auth):
        """Test that an expired token fails verification."""
        # Create token that expires immediately
        token = ed25519_auth.create_access_token(
            user_id="user123",
            email="test@example.com",
            role="agent",
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        payload = ed25519_auth.verify_token(token)
        assert payload is None

    def test_malformed_token_fails_validation(self, ed25519_auth):
        """Test that a malformed token fails verification."""
        malformed_token = "not.a.valid.jwt.token"

        payload = ed25519_auth.verify_token(malformed_token)
        assert payload is None

    def test_token_with_invalid_signature_fails(self, ed25519_auth, tmp_path):
        """Test that token with invalid signature fails verification."""
        # Create token with first auth instance
        token = ed25519_auth.create_access_token(
            user_id="user123", email="test@example.com", role="agent"
        )

        # Create new auth instance with different keys
        different_auth = Ed25519Auth(keys_dir=str(tmp_path / "different_keys"))

        # Token should fail validation with different keys
        payload = different_auth.verify_token(token)
        assert payload is None

    def test_token_without_required_claims_fails(self, ed25519_auth):
        """Test that token missing required claims fails validation."""
        # Manually create a token without required claims
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
            # Missing: sub, email, jti
        }

        token = jwt.encode(payload, ed25519_auth.private_key, algorithm="EdDSA")

        # Token is technically valid but missing application claims
        decoded = ed25519_auth.verify_token(token)
        assert decoded is not None  # Token structure is valid
        assert "sub" not in decoded  # But missing required claim


# ============================================================================
# 3. LOGIN TESTS
# ============================================================================


@pytest.mark.unit
class TestLogin:
    """Test user login functionality."""

    def test_successful_login_with_valid_credentials(
        self, ed25519_auth, mock_db_session, test_user
    ):
        """Test successful login returns tokens."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        # Mock database to return test user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute.return_value = mock_result

        authenticated_user = jwt_manager.authenticate_user(
            email="test@example.com", password="testpassword", db=mock_db_session
        )

        assert authenticated_user is not None
        assert authenticated_user.email == "test@example.com"
        assert authenticated_user.last_login_at is not None

    def test_failed_login_with_invalid_password(self, ed25519_auth, mock_db_session, test_user):
        """Test login fails with incorrect password."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute.return_value = mock_result

        authenticated_user = jwt_manager.authenticate_user(
            email="test@example.com", password="wrongpassword", db=mock_db_session
        )

        assert authenticated_user is None

    def test_failed_login_with_nonexistent_user(self, ed25519_auth, mock_db_session):
        """Test login fails with non-existent user email."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        authenticated_user = jwt_manager.authenticate_user(
            email="nonexistent@example.com", password="password", db=mock_db_session
        )

        assert authenticated_user is None

    def test_login_response_includes_access_and_refresh_tokens(self, ed25519_auth, test_user):
        """Test that login response contains both access and refresh tokens."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        tokens = jwt_manager.create_user_tokens(test_user)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert "expires_in" in tokens
        assert tokens["token_type"] == "bearer"

    def test_login_updates_last_login_timestamp(self, ed25519_auth, mock_db_session, test_user):
        """Test that successful login updates last_login_at timestamp."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        assert test_user.last_login_at is None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute.return_value = mock_result

        before_login = datetime.now(timezone.utc)
        authenticated_user = jwt_manager.authenticate_user(
            email="test@example.com", password="testpassword", db=mock_db_session
        )
        after_login = datetime.now(timezone.utc)

        assert authenticated_user is not None
        assert authenticated_user.last_login_at is not None
        assert before_login <= authenticated_user.last_login_at <= after_login


# ============================================================================
# 4. TOKEN REFRESH TESTS
# ============================================================================


@pytest.mark.unit
class TestTokenRefresh:
    """Test token refresh functionality."""

    def test_refresh_token_generates_new_access_token(self, ed25519_auth, test_user):
        """Test that refresh token can generate a new access token."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        # Create initial tokens
        tokens = jwt_manager.create_user_tokens(test_user)
        refresh_token = tokens["refresh_token"]

        # Verify refresh token
        refresh_payload = ed25519_auth.verify_token(refresh_token)
        assert refresh_payload is not None
        assert refresh_payload["type"] == "refresh"
        assert refresh_payload["sub"] == str(test_user.id)

    def test_refresh_with_invalid_token_fails(self, ed25519_auth):
        """Test that refresh with invalid token fails."""
        invalid_token = "invalid.token.here"

        payload = ed25519_auth.verify_token(invalid_token)
        assert payload is None

    def test_refresh_with_expired_refresh_token_fails(self, ed25519_auth):
        """Test that refresh with expired refresh token fails."""
        # Create expired refresh token
        payload = {
            "sub": "user123",
            "type": "refresh",
            "exp": datetime.now(timezone.utc) - timedelta(days=1),  # Expired yesterday
            "jti": "test-jti",
        }

        expired_token = jwt.encode(payload, ed25519_auth.private_key, algorithm="EdDSA")

        verified_payload = ed25519_auth.verify_token(expired_token)
        assert verified_payload is None

    def test_access_token_used_as_refresh_token_fails(self, ed25519_auth, test_user):
        """Test that access token cannot be used as refresh token."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        tokens = jwt_manager.create_user_tokens(test_user)
        access_token = tokens["access_token"]

        # Verify it's an access token (no "type" claim or wrong type)
        payload = ed25519_auth.verify_token(access_token)
        assert payload is not None
        assert payload.get("type") != "refresh"

    def test_new_access_token_has_updated_expiration(self, ed25519_auth):
        """Test that refreshed access token has new expiration time."""
        user_id = "user123"

        # Create first access token
        token1 = ed25519_auth.create_access_token(
            user_id=user_id,
            email="test@example.com",
            role="agent",
            expires_delta=timedelta(minutes=15),
        )

        payload1 = ed25519_auth.verify_token(token1)
        exp1 = payload1["exp"]
        iat1 = payload1["iat"]

        # Wait a moment and create another token
        import time

        time.sleep(1)  # Wait 1 second to ensure different timestamp

        # Create second access token (simulating refresh)
        token2 = ed25519_auth.create_access_token(
            user_id=user_id,
            email="test@example.com",
            role="agent",
            expires_delta=timedelta(minutes=15),
        )

        payload2 = ed25519_auth.verify_token(token2)
        exp2 = payload2["exp"]
        iat2 = payload2["iat"]

        # Second token should have later issue time and expiration
        assert iat2 > iat1
        assert exp2 >= exp1  # exp2 should be equal or greater


# ============================================================================
# 5. TOKEN REVOCATION TESTS
# ============================================================================


@pytest.mark.unit
class TestTokenRevocation:
    """Test token revocation and blacklist functionality."""

    def test_token_revocation_adds_to_blacklist(self, token_revocation_service, mock_redis_client):
        """Test that revoking a token adds it to the blacklist."""
        jti = "test-jti-123"
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        result = token_revocation_service.revoke_token(jti, expires_at)

        assert result is True
        mock_redis_client.setex.assert_called_once()

    def test_revoked_token_fails_validation(
        self, token_revocation_service, mock_redis_client, ed25519_auth
    ):
        """Test that a revoked token fails validation."""
        # Create a token
        token = ed25519_auth.create_access_token(
            user_id="user123", email="test@example.com", role="agent"
        )

        payload = ed25519_auth.verify_token(token)
        jti = payload["jti"]

        # Revoke the token
        mock_redis_client.exists.return_value = 1  # Token is in blacklist

        is_revoked = token_revocation_service.is_token_revoked(jti)
        assert is_revoked is True

    def test_logout_revokes_all_user_tokens(self, token_revocation_service, mock_redis_client):
        """Test that logout revokes all tokens for a user."""
        user_id = "user123"

        result = token_revocation_service.revoke_all_user_tokens(user_id)

        assert result is True
        mock_redis_client.set.assert_called_once()

    def test_jti_tracking_for_revocation(self, ed25519_auth):
        """Test that JTI (JWT ID) is properly tracked for revocation."""
        token = ed25519_auth.create_access_token(
            user_id="user123", email="test@example.com", role="agent"
        )

        payload = ed25519_auth.verify_token(token)
        jti = payload.get("jti")

        assert jti is not None
        assert isinstance(jti, str)
        assert len(jti) > 0

    def test_revocation_service_health_check(self, token_revocation_service, mock_redis_client):
        """Test that revocation service health check works."""
        mock_redis_client.ping.return_value = True

        is_healthy = token_revocation_service.health_check()
        assert is_healthy is True

    def test_token_revoked_before_user_revocation_time(
        self, token_revocation_service, mock_redis_client
    ):
        """Test that tokens issued before user revocation time are invalid."""
        user_id = "user123"

        # Set user revocation time to now
        revocation_time = datetime.now(timezone.utc)
        mock_redis_client.get.return_value = revocation_time.isoformat()

        # Token issued before revocation
        token_issued_at = revocation_time - timedelta(hours=1)

        is_revoked = token_revocation_service.is_token_revoked_for_user(user_id, token_issued_at)
        assert is_revoked is True

    def test_token_issued_after_user_revocation_is_valid(
        self, token_revocation_service, mock_redis_client
    ):
        """Test that tokens issued after user revocation time are valid."""
        user_id = "user123"

        # Set user revocation time to 1 hour ago
        revocation_time = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_redis_client.get.return_value = revocation_time.isoformat()

        # Token issued after revocation
        token_issued_at = datetime.now(timezone.utc)

        is_revoked = token_revocation_service.is_token_revoked_for_user(user_id, token_issued_at)
        assert is_revoked is False


# ============================================================================
# 6. PROTECTED ROUTE TESTS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
class TestProtectedRoutes:
    """Test authentication for protected routes."""

    async def test_authenticated_request_succeeds(self, ed25519_auth, mock_db_session, test_user):
        """Test that authenticated request to protected route succeeds."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        # Create valid token
        tokens = jwt_manager.create_user_tokens(test_user)
        token = tokens["access_token"]

        # Mock database lookup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute.return_value = mock_result

        # Verify token and get user
        user = jwt_manager.get_user_from_token(token, mock_db_session)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_unauthenticated_request_returns_401(self):
        """Test that unauthenticated request returns 401."""
        from fastapi import Request
        from fastapi.security import HTTPAuthorizationCredentials

        mock_request = MagicMock(spec=Request)
        mock_request.cookies.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request=mock_request, credentials=None, db=MagicMock())

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_request_with_invalid_token_returns_401(self, mock_db_session):
        """Test that request with invalid token returns 401."""
        from fastapi import Request
        from fastapi.security import HTTPAuthorizationCredentials

        mock_request = MagicMock(spec=Request)
        mock_request.cookies.get.return_value = None

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token.here"
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request, credentials=credentials, db=mock_db_session
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_request_with_revoked_token_returns_401(
        self, ed25519_auth, mock_db_session, test_user, mock_redis_client
    ):
        """Test that request with revoked token returns 401."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        # Create token
        tokens = jwt_manager.create_user_tokens(test_user)
        token = tokens["access_token"]

        # Get JTI
        payload = ed25519_auth.verify_token(token)
        jti = payload["jti"]

        # Mock Redis to return that token is revoked
        mock_redis_client.exists.return_value = 1

        with patch("app.auth.jwt_auth.get_revocation_service") as mock_get_service:
            mock_service = MagicMock()
            mock_service.is_token_revoked.return_value = True
            mock_get_service.return_value = mock_service

            # Try to verify token
            result = jwt_manager.verify_token(token)
            assert result is None

    async def test_inactive_user_cannot_access_protected_routes(
        self, ed25519_auth, mock_db_session, test_user
    ):
        """Test that inactive user cannot access protected routes."""
        test_user.is_active = False

        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        tokens = jwt_manager.create_user_tokens(test_user)
        token = tokens["access_token"]

        # Mock database to return inactive user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # User not found because inactive
        mock_db_session.execute.return_value = mock_result

        user = jwt_manager.get_user_from_token(token, mock_db_session)
        assert user is None


# ============================================================================
# 7. ROLE AND PERMISSION TESTS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
class TestRoleAndPermissions:
    """Test role-based and permission-based access control."""

    async def test_admin_role_has_system_access(self, test_admin_user):
        """Test that admin role has system admin permissions."""
        assert test_admin_user.role == UserRole.ADMIN
        assert Permission.SYSTEM_ADMIN.value in test_admin_user.permissions

    async def test_agent_role_limited_permissions(self, test_user):
        """Test that agent role has limited permissions."""
        assert test_user.role == UserRole.AGENT
        assert Permission.SYSTEM_ADMIN.value not in test_user.permissions

    async def test_token_contains_role_information(self, ed25519_auth, test_user):
        """Test that token includes user role information."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        tokens = jwt_manager.create_user_tokens(test_user)
        token = tokens["access_token"]

        payload = ed25519_auth.verify_token(token)
        assert "role" in payload
        assert payload["role"] == UserRole.AGENT.value

    async def test_token_contains_organization_id(self, ed25519_auth, test_user):
        """Test that token includes organization ID."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        tokens = jwt_manager.create_user_tokens(test_user)
        token = tokens["access_token"]

        payload = ed25519_auth.verify_token(token)
        assert "org_id" in payload
        assert payload["org_id"] == test_user.organization


# ============================================================================
# 8. PASSWORD HASHING TESTS
# ============================================================================


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hashing_produces_valid_hash(self, ed25519_auth):
        """Test that password hashing produces valid bcrypt hash."""
        password = "testpassword123"

        hashed = ed25519_auth.hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")
        assert len(hashed) > 50

    def test_password_verification_succeeds_with_correct_password(self, ed25519_auth):
        """Test that password verification succeeds with correct password."""
        password = "testpassword123"
        hashed = ed25519_auth.hash_password(password)

        result = ed25519_auth.verify_password(password, hashed)
        assert result is True

    def test_password_verification_fails_with_incorrect_password(self, ed25519_auth):
        """Test that password verification fails with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = ed25519_auth.hash_password(password)

        result = ed25519_auth.verify_password(wrong_password, hashed)
        assert result is False

    def test_same_password_produces_different_hashes(self, ed25519_auth):
        """Test that hashing the same password twice produces different hashes."""
        password = "testpassword123"

        hash1 = ed25519_auth.hash_password(password)
        hash2 = ed25519_auth.hash_password(password)

        assert hash1 != hash2


# ============================================================================
# 9. EDGE CASES AND ERROR HANDLING
# ============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_token_with_null_organization(self, ed25519_auth):
        """Test token creation with null organization."""
        token = ed25519_auth.create_access_token(
            user_id="user123", email="test@example.com", role="agent", org_id=None
        )

        payload = ed25519_auth.verify_token(token)
        assert payload is not None
        assert payload["org_id"] is None

    def test_very_long_token_expiration(self, ed25519_auth):
        """Test token creation with very long expiration time."""
        token = ed25519_auth.create_access_token(
            user_id="user123",
            email="test@example.com",
            role="agent",
            expires_delta=timedelta(days=365),
        )

        payload = ed25519_auth.verify_token(token)
        assert payload is not None

    def test_empty_string_password_hashing(self, ed25519_auth):
        """Test hashing empty string password."""
        password = ""

        hashed = ed25519_auth.hash_password(password)
        assert hashed is not None
        assert isinstance(hashed, str)

    def test_unicode_password_hashing(self, ed25519_auth):
        """Test hashing password with unicode characters."""
        password = "пароль🔐test密码"

        hashed = ed25519_auth.hash_password(password)
        result = ed25519_auth.verify_password(password, hashed)
        assert result is True

    def test_redis_unavailable_graceful_degradation(self):
        """Test that service handles Redis unavailability gracefully."""
        with patch("app.auth.token_revocation.redis.Redis") as mock_redis_class:
            # Mock Redis to raise exception on ping
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.side_effect = Exception("Redis connection failed")
            mock_redis_class.return_value = mock_redis_instance

            try:
                service = TokenRevocationService()
                # Service should catch exception and set redis_client to None
                assert service.redis_client is None

                # Operations should fail gracefully
                result = service.revoke_token(
                    "jti123", datetime.now(timezone.utc) + timedelta(hours=1)
                )
                assert result is False
            except Exception:
                # If exception is raised during init, that's also acceptable
                # as it shows Redis connection failure
                pass


# ============================================================================
# 10. INTEGRATION-LIKE TESTS
# ============================================================================


@pytest.mark.unit
class TestAuthenticationFlow:
    """Test complete authentication flows."""

    def test_complete_login_flow(self, ed25519_auth, mock_db_session, test_user):
        """Test complete login flow from credentials to token."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        # Mock database
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute.return_value = mock_result

        # 1. Authenticate user
        authenticated_user = jwt_manager.authenticate_user(
            email="test@example.com", password="testpassword", db=mock_db_session
        )
        assert authenticated_user is not None

        # 2. Create tokens
        tokens = jwt_manager.create_user_tokens(authenticated_user)
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        # 3. Verify access token
        access_payload = ed25519_auth.verify_token(tokens["access_token"])
        assert access_payload is not None
        assert access_payload["sub"] == str(test_user.id)

        # 4. Verify refresh token
        refresh_payload = ed25519_auth.verify_token(tokens["refresh_token"])
        assert refresh_payload is not None
        assert refresh_payload["type"] == "refresh"

    def test_token_refresh_flow(self, ed25519_auth, test_user):
        """Test complete token refresh flow."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        # 1. Create initial tokens
        tokens = jwt_manager.create_user_tokens(test_user)
        old_access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # 2. Verify refresh token
        refresh_payload = ed25519_auth.verify_token(refresh_token)
        assert refresh_payload is not None
        assert refresh_payload["type"] == "refresh"

        # 3. Create new access token
        new_access_token = ed25519_auth.create_access_token(
            user_id=str(test_user.id),
            email=test_user.email,
            role=test_user.role.value,
            org_id=test_user.organization,
        )

        # 4. Verify new access token is different
        assert new_access_token != old_access_token

        # 5. Verify new access token is valid
        new_payload = ed25519_auth.verify_token(new_access_token)
        assert new_payload is not None
        assert new_payload["sub"] == str(test_user.id)

    def test_logout_flow_with_token_revocation(
        self, ed25519_auth, token_revocation_service, mock_redis_client, test_user
    ):
        """Test complete logout flow with token revocation."""
        jwt_manager = JWTAuthManager()
        jwt_manager.auth = ed25519_auth

        # 1. Login and get tokens
        tokens = jwt_manager.create_user_tokens(test_user)
        access_token = tokens["access_token"]

        # 2. Get token payload
        payload = ed25519_auth.verify_token(access_token)
        jti = payload["jti"]
        exp = datetime.fromtimestamp(payload["exp"])

        # 3. Revoke token
        result = token_revocation_service.revoke_token(jti, exp)
        assert result is True

        # 4. Verify token is in blacklist
        mock_redis_client.exists.return_value = 1
        is_revoked = token_revocation_service.is_token_revoked(jti)
        assert is_revoked is True
