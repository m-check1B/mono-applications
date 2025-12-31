"""Tests for password reset functionality with dedicated tokens.

Uses shared test fixtures from conftest.py to ensure proper test isolation.
"""

import uuid
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.auth.database_routes import get_jwt_auth_manager


@pytest.fixture
def client(sync_test_engine):
    """Test client fixture that uses the test database."""
    # Override the get_db dependency to use test database
    from sqlalchemy.orm import sessionmaker
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# Use the shared sync_db_session fixture from conftest.py
# (aliased for backwards compatibility with test function signatures)
@pytest.fixture
def db_session(sync_db_session):
    """Database session fixture - delegates to shared fixture."""
    yield sync_db_session


@pytest.fixture
def email_service_mock(monkeypatch):
    """Mock email service"""

    class MockEmailService:
        def __init__(self):
            self.sent_emails = []

        def generate_verification_token(self):
            return "test_reset_token_123"

        def generate_token_expiration(self, hours=1):
            return datetime.now(timezone.utc) + timedelta(hours=hours)

        def send_password_reset_email(self, to_email, token, user_name=None):
            self.sent_emails.append(
                {"to": to_email, "token": token, "type": "reset", "user_name": user_name}
            )
            return True

    mock = MockEmailService()
    monkeypatch.setattr("app.services.email_service.EmailService", MockEmailService)
    monkeypatch.setattr("app.services.email_service._email_service", mock)
    return mock


def test_forgot_password_sends_email_with_new_token_fields(client, db_session, email_service_mock):
    """Test forgot password sends email using new password reset token fields"""
    auth_manager = get_jwt_auth_manager()

    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        password_hash=auth_manager.hash_password("oldpass123"),
        full_name="Test User",
        role="USER",
        is_active=True,
        is_verified=True,
        password_changed_at=datetime.now(timezone.utc),
        permissions=[],
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/api/v1/auth/forgot-password", json={"email": "test@example.com"})

    assert response.status_code == 200
    assert len(email_service_mock.sent_emails) == 1
    assert email_service_mock.sent_emails[0]["to"] == test_email
    assert email_service_mock.sent_emails[0]["type"] == "reset"

    db_session.refresh(user)
    assert user.password_reset_token == "test_reset_token_123"
    assert user.password_reset_token_expires is not None
    assert user.email_verification_token is None


def test_reset_password_with_new_token_fields(client, db_session, email_service_mock):
    """Test password reset with new dedicated token fields"""
    auth_manager = get_jwt_auth_manager()
    old_hash = auth_manager.hash_password("oldpass123")

    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        password_hash=old_hash,
        full_name="Test User",
        role="USER",
        is_active=True,
        is_verified=True,
        password_reset_token="valid_reset_token",
        password_reset_token_expires=datetime.now(timezone.utc) + timedelta(hours=1),
        password_changed_at=datetime.now(timezone.utc),
        permissions=[],
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "valid_reset_token", "new_password": "newpass123"},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Password reset successfully"

    db_session.refresh(user)
    assert user.password_hash != old_hash
    assert user.password_reset_token is None
    assert user.password_reset_token_expires is None


def test_reset_password_with_expired_new_token(client, db_session, email_service_mock):
    """Test password reset with expired token using new fields"""
    auth_manager = get_jwt_auth_manager()

    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        password_hash=auth_manager.hash_password("oldpass123"),
        full_name="Test User",
        role="USER",
        is_active=True,
        is_verified=True,
        password_reset_token="expired_reset_token",
        password_reset_token_expires=datetime.now(timezone.utc) - timedelta(hours=1),
        password_changed_at=datetime.now(timezone.utc),
        permissions=[],
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "expired_reset_token", "new_password": "newpass123"},
    )

    assert response.status_code == 400
    assert "Token has expired" in response.json()["detail"]


def test_email_verification_and_password_reset_dont_conflict(
    client, db_session, email_service_mock
):
    """Test that email verification and password reset tokens don't conflict"""
    from app.auth.database_routes import UserRegister

    auth_manager = get_jwt_auth_manager()

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
            "organization": "Test Org",
        },
    )

    assert response.status_code == 200
    user = db_session.query(User).filter(User.email.like(f"test-%@example.com")).first()
    assert user is not None
    assert user.is_verified is False

    user.email_verification_token = "email_verify_token"
    user.email_verification_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    db_session.commit()

    response = client.post("/api/v1/auth/forgot-password", json={"email": "test@example.com"})
    assert response.status_code == 200

    db_session.refresh(user)
    assert user.email_verification_token == "email_verify_token"
    assert user.email_verification_token_expires is not None
    assert user.password_reset_token == "test_reset_token_123"
    assert user.password_reset_token_expires is not None


def test_reset_password_resets_failed_attempts_and_lock(client, db_session, email_service_mock):
    """Test that password reset clears failed login attempts and lock"""
    auth_manager = get_jwt_auth_manager()

    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        password_hash=auth_manager.hash_password("oldpass123"),
        full_name="Test User",
        role="USER",
        is_active=True,
        is_verified=True,
        password_reset_token="valid_reset_token",
        password_reset_token_expires=datetime.now(timezone.utc) + timedelta(hours=1),
        failed_login_attempts=5,
        locked_until=datetime.now(timezone.utc) + timedelta(hours=1),
        password_changed_at=datetime.now(timezone.utc),
        permissions=[],
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "valid_reset_token", "new_password": "newpass123"},
    )

    assert response.status_code == 200

    db_session.refresh(user)
    assert user.failed_login_attempts == 0
    assert user.locked_until is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
