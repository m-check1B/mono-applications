"""Tests for SECRET_KEY validation in settings.

VD-362: Hardcoded insecure secret key in settings.py
This test suite verifies that the application properly validates SECRET_KEY
in different environments.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError


class TestSecretKeyValidation:
    """Test suite for SECRET_KEY validation."""

    @pytest.fixture(autouse=True)
    def clear_settings_cache(self):
        """Clear the settings cache before each test."""
        from app.config.settings import get_settings
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()

    def test_empty_key_rejected_in_production(self):
        """Empty SECRET_KEY should be rejected in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": ""}):
            from app.config.settings import Settings
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "SECRET_KEY is required in production" in str(exc_info.value)

    def test_weak_key_rejected_in_production(self):
        """Weak SECRET_KEY patterns should be rejected in production."""
        weak_keys = [
            "insecure-dev-secret-key-change-in-production",
            "changeme123456789",
            "your_secret_here",
            "placeholder12345678",
            "xxx1234567890123456",
            "example-secret-key-here",
        ]
        for weak_key in weak_keys:
            with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": weak_key}):
                from app.config.settings import Settings
                with pytest.raises(ValidationError):
                    Settings()

    def test_short_key_rejected_in_production(self):
        """Keys shorter than 16 characters should be rejected in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": "short"}):
            from app.config.settings import Settings
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "SECRET_KEY is required in production" in str(exc_info.value)

    def test_strong_key_accepted_in_production(self):
        """A strong random key should be accepted in production."""
        import secrets
        strong_key = secrets.token_urlsafe(32)
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": strong_key}):
            from app.config.settings import Settings
            settings = Settings()
            assert settings.secret_key == strong_key

    def test_empty_key_allowed_in_development(self):
        """Empty SECRET_KEY should be allowed in development (with fallback)."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development", "SECRET_KEY": ""}):
            from app.config.settings import Settings
            settings = Settings()
            assert "dev-only-insecure" in settings.secret_key
            assert "DO-NOT-USE-IN-PRODUCTION" in settings.secret_key

    def test_weak_key_allowed_in_development(self):
        """Weak keys should be allowed in development (with warning)."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development", "SECRET_KEY": "insecure-dev-key"}):
            from app.config.settings import Settings
            settings = Settings()
            # Key should be accepted (not raise)
            assert settings.secret_key == "insecure-dev-key"

    def test_no_default_hardcoded_key(self):
        """The Settings class should not have an insecure default hardcoded."""
        from app.config.settings import Settings
        # Check the Field definition
        field = Settings.model_fields.get("secret_key")
        assert field is not None
        # The default should be empty string (not a hardcoded insecure value)
        assert field.default == ""
