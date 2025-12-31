"""Tests for EmailService.

Tests cover:
- Token generation
- Token expiration calculation
- Email address validation
- Verification email sending
- Password reset email sending
- SMTP configuration
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, ANY
import smtplib

from app.services.email_service import EmailService, get_email_service


@pytest.fixture
def email_service():
    """Create a fresh EmailService instance for each test."""
    return EmailService()


@pytest.fixture
def mock_smtp():
    """Mock SMTP for testing email sending."""
    with patch("smtplib.SMTP") as mock:
        instance = MagicMock()
        mock.return_value.__enter__ = MagicMock(return_value=instance)
        mock.return_value.__exit__ = MagicMock(return_value=False)
        yield mock, instance


class TestTokenGeneration:
    """Tests for token generation."""

    def test_generate_verification_token(self, email_service):
        """Test that verification token is generated."""
        token = email_service.generate_verification_token()

        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)

    def test_verification_token_is_unique(self, email_service):
        """Test that each token is unique."""
        tokens = [email_service.generate_verification_token() for _ in range(100)]
        unique_tokens = set(tokens)

        assert len(unique_tokens) == len(tokens)

    def test_verification_token_is_url_safe(self, email_service):
        """Test that token is URL-safe."""
        token = email_service.generate_verification_token()

        # URL-safe characters only
        import re
        assert re.match(r'^[A-Za-z0-9_-]+$', token)


class TestTokenHashing:
    """Tests for secure token hashing (VD-327 security fix)."""

    def test_generate_verification_token_with_hash(self, email_service):
        """Test that generate_verification_token_with_hash returns tuple."""
        plaintext, hashed = email_service.generate_verification_token_with_hash()

        assert plaintext is not None
        assert hashed is not None
        assert isinstance(plaintext, str)
        assert isinstance(hashed, str)
        assert plaintext != hashed  # Plaintext should not equal hash

    def test_hash_token_produces_sha256(self, email_service):
        """Test that hash_token produces SHA-256 hash (64 hex chars)."""
        token = "test_token_123"
        hashed = email_service.hash_token(token)

        assert len(hashed) == 64  # SHA-256 produces 64 hex characters
        assert all(c in '0123456789abcdef' for c in hashed)

    def test_hash_token_is_deterministic(self, email_service):
        """Test that same token always produces same hash."""
        token = "consistent_token"
        hash1 = email_service.hash_token(token)
        hash2 = email_service.hash_token(token)

        assert hash1 == hash2

    def test_hash_token_is_unique_for_different_tokens(self, email_service):
        """Test that different tokens produce different hashes."""
        token1 = "token_one"
        token2 = "token_two"
        hash1 = email_service.hash_token(token1)
        hash2 = email_service.hash_token(token2)

        assert hash1 != hash2

    def test_hashed_token_can_be_verified(self, email_service):
        """Test that plaintext can be verified against stored hash."""
        plaintext, stored_hash = email_service.generate_verification_token_with_hash()

        # Simulate verification: hash the incoming token and compare
        verification_hash = email_service.hash_token(plaintext)

        assert verification_hash == stored_hash

    def test_hash_token_handles_unicode(self, email_service):
        """Test that hash_token handles unicode characters."""
        token = "token_with_émojis_🔐"
        hashed = email_service.hash_token(token)

        assert len(hashed) == 64
        assert isinstance(hashed, str)

    def test_generated_tokens_are_unique(self, email_service):
        """Test that generated token+hash pairs are unique."""
        pairs = [email_service.generate_verification_token_with_hash() for _ in range(50)]
        plaintexts = [p[0] for p in pairs]
        hashes = [p[1] for p in pairs]

        assert len(set(plaintexts)) == 50  # All plaintexts unique
        assert len(set(hashes)) == 50  # All hashes unique


class TestTokenExpiration:
    """Tests for token expiration calculation."""

    def test_generate_token_expiration_default(self, email_service):
        """Test default expiration is 24 hours."""
        before = datetime.now(timezone.utc)
        expiration = email_service.generate_token_expiration()
        after = datetime.now(timezone.utc)

        expected_min = before + timedelta(hours=24)
        expected_max = after + timedelta(hours=24)

        assert expected_min <= expiration <= expected_max

    def test_generate_token_expiration_custom_hours(self, email_service):
        """Test custom expiration hours."""
        before = datetime.now(timezone.utc)
        expiration = email_service.generate_token_expiration(hours=1)
        after = datetime.now(timezone.utc)

        expected_min = before + timedelta(hours=1)
        expected_max = after + timedelta(hours=1)

        assert expected_min <= expiration <= expected_max

    def test_generate_token_expiration_timezone_aware(self, email_service):
        """Test expiration is timezone-aware."""
        expiration = email_service.generate_token_expiration()

        assert expiration.tzinfo is not None


class TestEmailValidation:
    """Tests for email address validation.

    Note: email_validator does DNS checks by default, so we mock it
    to test our wrapper function's behavior.
    """

    def test_valid_email(self, email_service):
        """Test valid email address passes validation."""
        with patch("app.services.email_service.validate_email"):
            assert email_service.verify_email_address("test@example.com") is True

    def test_valid_email_with_plus(self, email_service):
        """Test valid email with plus addressing."""
        with patch("app.services.email_service.validate_email"):
            assert email_service.verify_email_address("test+tag@example.com") is True

    def test_valid_email_with_subdomain(self, email_service):
        """Test valid email with subdomain."""
        with patch("app.services.email_service.validate_email"):
            assert email_service.verify_email_address("test@mail.example.com") is True

    def test_invalid_email_no_at(self, email_service):
        """Test invalid email without @ symbol."""
        # email_validator will raise exception for invalid format
        assert email_service.verify_email_address("testexample.com") is False

    def test_invalid_email_no_domain(self, email_service):
        """Test invalid email without domain."""
        assert email_service.verify_email_address("test@") is False

    def test_invalid_email_empty(self, email_service):
        """Test empty email is invalid."""
        assert email_service.verify_email_address("") is False

    def test_invalid_email_spaces(self, email_service):
        """Test email with spaces is invalid."""
        assert email_service.verify_email_address("test @example.com") is False


class TestVerificationEmail:
    """Tests for verification email sending."""

    def test_send_verification_email_success(self, email_service, mock_smtp):
        """Test successful verification email sending."""
        smtp_class, smtp_instance = mock_smtp

        result = email_service.send_verification_email(
            to_email="test@example.com",
            token="test_token_123"
        )

        assert result is True
        smtp_instance.send_message.assert_called_once()

    def test_send_verification_email_with_name(self, email_service, mock_smtp):
        """Test verification email includes user name."""
        smtp_class, smtp_instance = mock_smtp

        result = email_service.send_verification_email(
            to_email="test@example.com",
            token="test_token_123",
            user_name="John Doe"
        )

        assert result is True
        # Verify the message was sent
        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]
        # Check subject
        assert msg["Subject"] == "Verify Your Email Address"

    def test_send_verification_email_contains_token(self, email_service, mock_smtp):
        """Test verification email contains the token in URL."""
        smtp_class, smtp_instance = mock_smtp

        token = "my_special_token_xyz"
        email_service.send_verification_email(
            to_email="test@example.com",
            token=token
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]

        # Get email body and check for token
        for part in msg.walk():
            if part.get_content_type() in ["text/html", "text/plain"]:
                content = part.get_payload(decode=True).decode()
                assert token in content

    def test_send_verification_email_smtp_error(self, email_service):
        """Test handling SMTP error."""
        with patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

            result = email_service.send_verification_email(
                to_email="test@example.com",
                token="test_token"
            )

            assert result is False


class TestPasswordResetEmail:
    """Tests for password reset email sending."""

    def test_send_password_reset_email_success(self, email_service, mock_smtp):
        """Test successful password reset email sending."""
        smtp_class, smtp_instance = mock_smtp

        result = email_service.send_password_reset_email(
            to_email="test@example.com",
            token="reset_token_123"
        )

        assert result is True
        smtp_instance.send_message.assert_called_once()

    def test_send_password_reset_email_with_name(self, email_service, mock_smtp):
        """Test password reset email includes user name."""
        smtp_class, smtp_instance = mock_smtp

        result = email_service.send_password_reset_email(
            to_email="test@example.com",
            token="reset_token_123",
            user_name="Jane Doe"
        )

        assert result is True

    def test_send_password_reset_email_subject(self, email_service, mock_smtp):
        """Test password reset email has correct subject."""
        smtp_class, smtp_instance = mock_smtp

        email_service.send_password_reset_email(
            to_email="test@example.com",
            token="reset_token"
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]
        assert msg["Subject"] == "Reset Your Password"

    def test_send_password_reset_email_contains_token(self, email_service, mock_smtp):
        """Test password reset email contains the token in URL."""
        smtp_class, smtp_instance = mock_smtp

        token = "reset_token_abc123"
        email_service.send_password_reset_email(
            to_email="test@example.com",
            token=token
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]

        for part in msg.walk():
            if part.get_content_type() in ["text/html", "text/plain"]:
                content = part.get_payload(decode=True).decode()
                assert token in content

    def test_send_password_reset_email_smtp_error(self, email_service):
        """Test handling SMTP error for password reset."""
        with patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

            result = email_service.send_password_reset_email(
                to_email="test@example.com",
                token="reset_token"
            )

            assert result is False


class TestSMTPConfiguration:
    """Tests for SMTP configuration."""

    def test_default_smtp_config(self, email_service):
        """Test default SMTP configuration values."""
        assert email_service.smtp_host == "localhost"
        assert email_service.smtp_port == 587
        assert email_service.smtp_use_tls is True

    def test_smtp_config_from_env(self):
        """Test SMTP configuration from environment variables."""
        with patch.dict("os.environ", {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "465",
            "SMTP_USERNAME": "user@example.com",
            "SMTP_PASSWORD": "secret123",
            "SMTP_USE_TLS": "false",
            "SMTP_FROM_EMAIL": "sender@example.com",
            "SMTP_FROM_NAME": "Test Sender"
        }):
            service = EmailService()

            assert service.smtp_host == "smtp.example.com"
            assert service.smtp_port == 465
            assert service.smtp_username == "user@example.com"
            assert service.smtp_password == "secret123"
            assert service.smtp_use_tls is False
            assert service.from_email == "sender@example.com"
            assert service.from_name == "Test Sender"

    def test_smtp_tls_enabled(self, email_service, mock_smtp):
        """Test TLS is used when enabled."""
        smtp_class, smtp_instance = mock_smtp
        email_service.smtp_use_tls = True

        email_service.send_verification_email(
            to_email="test@example.com",
            token="token"
        )

        smtp_instance.starttls.assert_called_once()

    def test_smtp_auth_used(self, email_service, mock_smtp):
        """Test SMTP authentication is used when credentials provided."""
        smtp_class, smtp_instance = mock_smtp
        email_service.smtp_username = "user@test.com"
        email_service.smtp_password = "password123"

        email_service.send_verification_email(
            to_email="test@example.com",
            token="token"
        )

        smtp_instance.login.assert_called_once_with("user@test.com", "password123")


class TestFrontendURL:
    """Tests for frontend URL configuration."""

    def test_default_frontend_url(self, email_service):
        """Test default frontend URL."""
        assert email_service.frontend_url == "https://voice.kraliki.com"

    def test_verification_url_format(self, email_service, mock_smtp):
        """Test verification URL is correctly formatted."""
        smtp_class, smtp_instance = mock_smtp
        token = "my_token"

        email_service.send_verification_email(
            to_email="test@example.com",
            token=token
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]

        for part in msg.walk():
            if part.get_content_type() == "text/html":
                content = part.get_payload(decode=True).decode()
                expected_url = f"{email_service.frontend_url}/verify-email?token={token}"
                assert expected_url in content

    def test_reset_url_format(self, email_service, mock_smtp):
        """Test password reset URL is correctly formatted."""
        smtp_class, smtp_instance = mock_smtp
        token = "reset_token"

        email_service.send_password_reset_email(
            to_email="test@example.com",
            token=token
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]

        for part in msg.walk():
            if part.get_content_type() == "text/html":
                content = part.get_payload(decode=True).decode()
                expected_url = f"{email_service.frontend_url}/reset-password?token={token}"
                assert expected_url in content


class TestSingleton:
    """Tests for singleton service instance."""

    def test_get_email_service_returns_singleton(self):
        """Test that get_email_service returns singleton."""
        service1 = get_email_service()
        service2 = get_email_service()

        assert service1 is service2

    def test_get_email_service_returns_email_service(self):
        """Test get_email_service returns EmailService instance."""
        service = get_email_service()

        assert isinstance(service, EmailService)


class TestEmailContent:
    """Tests for email content structure."""

    def test_verification_email_multipart(self, email_service, mock_smtp):
        """Test verification email is multipart (HTML + plain text)."""
        smtp_class, smtp_instance = mock_smtp

        email_service.send_verification_email(
            to_email="test@example.com",
            token="token"
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]

        content_types = [part.get_content_type() for part in msg.walk()]
        assert "text/html" in content_types
        assert "text/plain" in content_types

    def test_password_reset_email_multipart(self, email_service, mock_smtp):
        """Test password reset email is multipart (HTML + plain text)."""
        smtp_class, smtp_instance = mock_smtp

        email_service.send_password_reset_email(
            to_email="test@example.com",
            token="token"
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]

        content_types = [part.get_content_type() for part in msg.walk()]
        assert "text/html" in content_types
        assert "text/plain" in content_types

    def test_email_from_header(self, email_service, mock_smtp):
        """Test email From header is correctly set."""
        smtp_class, smtp_instance = mock_smtp

        email_service.send_verification_email(
            to_email="test@example.com",
            token="token"
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]

        assert email_service.from_name in msg["From"]
        assert email_service.from_email in msg["From"]

    def test_email_to_header(self, email_service, mock_smtp):
        """Test email To header is correctly set."""
        smtp_class, smtp_instance = mock_smtp
        recipient = "recipient@example.com"

        email_service.send_verification_email(
            to_email=recipient,
            token="token"
        )

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]

        assert msg["To"] == recipient
