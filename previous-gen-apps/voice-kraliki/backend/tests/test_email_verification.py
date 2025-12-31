"""Tests for email verification functionality.

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
from app.auth.database_routes import UserRegister
from app.services.email_service import get_email_service


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
            return "test_token_123"

        def generate_token_expiration(self, hours=24):
            return datetime.now(timezone.utc) + timedelta(hours=hours)

        def send_verification_email(self, to_email, token, user_name=None):
            self.sent_emails.append(
                {"to": to_email, "token": token, "type": "verification", "user_name": user_name}
            )
            return True

        def send_password_reset_email(self, to_email, token, user_name=None):
            self.sent_emails.append(
                {"to": to_email, "token": token, "type": "reset", "user_name": user_name}
            )
            return True

    mock = MockEmailService()
    monkeypatch.setattr("app.services.email_service.EmailService", MockEmailService)
    monkeypatch.setattr("app.services.email_service._email_service", mock)
    return mock


def test_register_creates_unverified_user(client, db_session):
    """Test that registration creates unverified user"""
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


def test_verify_email_with_valid_token(client, db_session, email_service_mock):
    """Test email verification with valid token"""
    from app.auth.database_routes import get_jwt_auth_manager

    auth_manager = get_jwt_auth_manager()

    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        password_hash=auth_manager.hash_password("testpass123"),
        full_name="Test User",
        role="USER",
        is_active=True,
        is_verified=False,
        email_verification_token="valid_token",
        email_verification_token_expires=datetime.now(timezone.utc) + timedelta(hours=1),
        password_changed_at=datetime.now(timezone.utc),
        permissions=[],
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/api/v1/auth/verify-email/valid_token")

    assert response.status_code == 200
    assert response.json()["detail"] == "Email verified successfully"

    db_session.refresh(user)
    assert user.is_verified is True
    assert user.email_verification_token is None
    assert user.email_verification_token_expires is None


def test_verify_email_with_invalid_token(client, db_session):
    """Test email verification with invalid token"""
    response = client.post("/api/v1/auth/verify-email/invalid_token")

    assert response.status_code == 404
    assert "Invalid or expired token" in response.json()["detail"]


def test_verify_email_with_expired_token(client, db_session):
    """Test email verification with expired token"""
    from app.auth.database_routes import get_jwt_auth_manager

    auth_manager = get_jwt_auth_manager()

    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        password_hash=auth_manager.hash_password("testpass123"),
        full_name="Test User",
        role="USER",
        is_active=True,
        is_verified=False,
        email_verification_token="expired_token",
        email_verification_token_expires=datetime.now(timezone.utc) - timedelta(hours=1),
        password_changed_at=datetime.now(timezone.utc),
        permissions=[],
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/api/v1/auth/verify-email/expired_token")

    assert response.status_code == 400
    assert "Token has expired" in response.json()["detail"]


def test_forgot_password_sends_email(client, db_session, email_service_mock):
    """Test forgot password sends email"""
    from app.auth.database_routes import get_jwt_auth_manager

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


def test_reset_password_with_valid_token(client, db_session, email_service_mock):
    """Test password reset with valid token"""
    from app.auth.database_routes import get_jwt_auth_manager

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


def test_reset_password_with_weak_password(client, db_session):
    """Test password reset with weak password"""
    response = client.post(
        "/api/v1/auth/reset-password", json={"token": "some_token", "new_password": "short"}
    )

    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
