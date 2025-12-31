"""
Configuration Tests - Settings and environment variables
Tests configuration loading, validation, and security checks
"""

import os
import pytest
from unittest.mock import patch
import sys

from app.core.config import Settings, settings


class TestSettingsDefaults:
    """Test default configuration values"""

    def test_database_url_default(self):
        """Default DATABASE_URL should be SQLite"""
        test_settings = Settings()
        assert test_settings.DATABASE_URL == "sqlite:///./focus_kraliki.db"

    def test_jwt_algorithm_default(self):
        """Default JWT algorithm should be HS256"""
        test_settings = Settings()
        assert test_settings.JWT_ALGORITHM == "HS256"

    def test_access_token_expiry_default(self):
        """Default access token expiry should be 15 minutes"""
        test_settings = Settings()
        assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15

    def test_refresh_token_expiry_default(self):
        """Default refresh token expiry should be 7 days"""
        test_settings = Settings()
        assert test_settings.REFRESH_TOKEN_EXPIRE_DAYS == 7

    def test_host_default(self):
        """Default host should be 127.0.0.1"""
        test_settings = Settings()
        assert test_settings.HOST == "127.0.0.1"

    def test_port_default(self):
        """Default port should be 3017"""
        test_settings = Settings()
        assert test_settings.PORT == 3017

    def test_environment_default(self):
        """Default environment should be development"""
        test_settings = Settings()
        assert test_settings.ENVIRONMENT == "development"

    def test_debug_default(self):
        """Default DEBUG should be False"""
        test_settings = Settings()
        assert test_settings.DEBUG is False

    def test_platform_mode_default(self):
        """Default PLATFORM_MODE should be False"""
        test_settings = Settings()
        assert test_settings.PLATFORM_MODE is False

    def test_use_inmemory_events_default(self):
        """Default USE_INMEMORY_EVENTS should be False"""
        test_settings = Settings()
        assert test_settings.USE_INMEMORY_EVENTS is False

    def test_enable_calendar_integration_default(self):
        """Default ENABLE_CALENDAR_INTEGRATION should be False"""
        test_settings = Settings()
        assert test_settings.ENABLE_CALENDAR_INTEGRATION is False


class TestSettingsEnvironmentOverrides:
    """Test environment variable overrides"""

    def test_database_url_override(self):
        """DATABASE_URL can be overridden via environment"""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test"}):
            test_settings = Settings()
            assert test_settings.DATABASE_URL == "postgresql://test"

    def test_jwt_secret_override(self):
        """JWT_SECRET can be overridden via environment"""
        custom_secret = "custom-secret-key-32-chars-long"
        with patch.dict(os.environ, {"JWT_SECRET": custom_secret}):
            test_settings = Settings()
            assert test_settings.JWT_SECRET == custom_secret

    def test_redis_url_override(self):
        """REDIS_URL can be overridden via environment"""
        with patch.dict(os.environ, {"REDIS_URL": "redis://custom:6379/1"}):
            test_settings = Settings()
            assert test_settings.REDIS_URL == "redis://custom:6379/1"

    def test_environment_override(self):
        """ENVIRONMENT can be overridden via environment"""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            test_settings = Settings()
            assert test_settings.ENVIRONMENT == "production"

    def test_allowed_origins_override(self):
        """ALLOWED_ORIGINS can be overridden via environment"""
        custom_origins = "http://example1.com,http://example2.com"
        with patch.dict(os.environ, {"ALLOWED_ORIGINS": custom_origins}):
            test_settings = Settings()
            assert test_settings.ALLOWED_ORIGINS == custom_origins


class TestSettingsOptionalValues:
    """Test optional configuration values can be None"""

    def test_anthropic_api_key_optional(self):
        """ANTHROPIC_API_KEY is optional"""
        test_settings = Settings()
        assert test_settings.ANTHROPIC_API_KEY is None or isinstance(
            test_settings.ANTHROPIC_API_KEY, str
        )

    def test_gemini_api_key_optional(self):
        """GEMINI_API_KEY is optional"""
        test_settings = Settings()
        assert test_settings.GEMINI_API_KEY is None or isinstance(
            test_settings.GEMINI_API_KEY, str
        )

    def test_stripe_secret_key_optional(self):
        """STRIPE_SECRET_KEY is optional"""
        test_settings = Settings()
        assert test_settings.STRIPE_SECRET_KEY is None or isinstance(
            test_settings.STRIPE_SECRET_KEY, str
        )

    def test_google_oauth_optional(self):
        """Google OAuth credentials are optional"""
        test_settings = Settings()
        assert test_settings.GOOGLE_OAUTH_CLIENT_ID is None or isinstance(
            test_settings.GOOGLE_OAUTH_CLIENT_ID, str
        )
        assert test_settings.GOOGLE_OAUTH_CLIENT_SECRET is None or isinstance(
            test_settings.GOOGLE_OAUTH_CLIENT_SECRET, str
        )


class TestOriginsListProperty:
    """Test origins_list property parsing"""

    def test_origins_list_single_origin(self):
        """Single origin should be parsed correctly"""
        with patch.dict(os.environ, {"ALLOWED_ORIGINS": "http://localhost:5173"}):
            test_settings = Settings()
            origins = test_settings.origins_list
            assert origins == ["http://localhost:5173"]

    def test_origins_list_multiple_origins(self):
        """Multiple origins should be parsed correctly"""
        with patch.dict(
            os.environ, {"ALLOWED_ORIGINS": "http://localhost:5173,http://example.com"}
        ):
            test_settings = Settings()
            origins = test_settings.origins_list
            assert origins == ["http://localhost:5173", "http://example.com"]

    def test_origins_list_trims_whitespace(self):
        """Origins with extra spaces should be trimmed"""
        with patch.dict(
            os.environ,
            {"ALLOWED_ORIGINS": " http://localhost:5173 , http://example.com "},
        ):
            test_settings = Settings()
            origins = test_settings.origins_list
            assert origins == ["http://localhost:5173", "http://example.com"]


class TestSettingsModelConfiguration:
    """Test pydantic model configuration"""

    def test_case_sensitive(self):
        """Settings should be case sensitive"""
        test_settings = Settings()
        assert test_settings.model_config["case_sensitive"] is True

    def test_extra_ignore(self):
        """Extra fields should be ignored"""
        test_settings = Settings()
        assert test_settings.model_config["extra"] == "ignore"

    def test_env_file_set(self):
        """env_file should be set"""
        test_settings = Settings()
        assert ".env" in test_settings.model_config.get("env_file", "")


class TestSettingsValidation:
    """Test settings validation logic"""

    def test_production_requires_non_default_secret(self, caplog):
        """Production environment should reject default JWT secret"""
        # Clear any existing env vars that might interfere
        env_backup = os.environ.copy()
        os.environ.clear()

        try:
            # Set production environment with default secret
            with patch.dict(
                os.environ,
                {
                    "ENVIRONMENT": "production",
                    "JWT_SECRET": "replit-default-secret-change-in-production-min-32-chars",
                },
                clear=True,
            ):
                # This should call sys.exit(1) with critical log
                with pytest.raises(SystemExit) as exc_info:
                    from app.core.config import settings as reloaded_settings

                assert exc_info.value.code == 1
        finally:
            os.environ.update(env_backup)

    def test_production_requires_minimum_secret_length(self):
        """Production environment should reject short JWT secret"""
        env_backup = os.environ.copy()
        os.environ.clear()

        try:
            with patch.dict(
                os.environ,
                {"ENVIRONMENT": "production", "JWT_SECRET": "short", "DEBUG": "false"},
                clear=True,
            ):
                with pytest.raises(SystemExit) as exc_info:
                    from app.core.config import settings as reloaded_settings

                assert exc_info.value.code == 1
        finally:
            os.environ.update(env_backup)

    def test_production_rejects_debug_true(self):
        """Production environment should reject DEBUG=True"""
        env_backup = os.environ.copy()
        os.environ.clear()

        try:
            with patch.dict(
                os.environ,
                {
                    "ENVIRONMENT": "production",
                    "JWT_SECRET": "sufficiently-long-secret-key-for-production-32",
                    "DEBUG": "true",
                },
                clear=True,
            ):
                with pytest.raises(SystemExit) as exc_info:
                    from app.core.config import settings as reloaded_settings

                assert exc_info.value.code == 1
        finally:
            os.environ.update(env_backup)

    def test_development_allows_default_secret(self):
        """Development environment should allow default secret"""
        env_backup = os.environ.copy()
        os.environ.clear()

        try:
            with patch.dict(
                os.environ,
                {
                    "ENVIRONMENT": "development",
                    "JWT_SECRET": "replit-default-secret-change-in-production-min-32-chars",
                    "DEBUG": "false",
                },
                clear=True,
            ):
                # Should not raise SystemExit
                from app.core.config import settings as reloaded_settings

                assert reloaded_settings is not None
        finally:
            os.environ.update(env_backup)


class TestSettingsInstance:
    """Test singleton settings instance"""

    def test_settings_instance_exists(self):
        """Settings instance should be available"""
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_settings_has_required_attributes(self):
        """Settings should have all required attributes"""
        required_attrs = [
            "DATABASE_URL",
            "JWT_SECRET",
            "JWT_ALGORITHM",
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "REDIS_URL",
            "ENVIRONMENT",
            "DEBUG",
            "HOST",
            "PORT",
        ]
        for attr in required_attrs:
            assert hasattr(settings, attr)


class TestBrainModelSettings:
    """Test Brain AI model configuration"""

    def test_brain_model_default(self):
        """Default BRAIN_MODEL should be Z.AI GLM-4.7"""
        test_settings = Settings()
        assert test_settings.BRAIN_MODEL == "zhipu/glm-4-plus"

    def test_brain_model_provider_default(self):
        """Default BRAIN_MODEL_PROVIDER should be openrouter"""
        test_settings = Settings()
        assert test_settings.BRAIN_MODEL_PROVIDER == "openrouter"

    def test_brain_fallback_model_default(self):
        """Default BRAIN_FALLBACK_MODEL should be Gemini Flash"""
        test_settings = Settings()
        assert test_settings.BRAIN_FALLBACK_MODEL == "google/gemini-2.0-flash-001"

    def test_voice_transcription_model_default(self):
        """Default VOICE_TRANSCRIPTION_MODEL should be Gemini Flash"""
        test_settings = Settings()
        assert test_settings.VOICE_TRANSCRIPTION_MODEL == "google/gemini-2.0-flash-001"


class TestTokenExpirySettings:
    """Test token expiry configuration"""

    def test_agent_token_expiry_default(self):
        """Default AGENT_TOKEN_EXPIRE_MINUTES should be 120"""
        test_settings = Settings()
        assert test_settings.AGENT_TOKEN_EXPIRE_MINUTES == 120

    def test_token_expiry_can_be_overridden(self):
        """Token expiry settings can be overridden"""
        with patch.dict(
            os.environ,
            {
                "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
                "REFRESH_TOKEN_EXPIRE_DAYS": "14",
                "AGENT_TOKEN_EXPIRE_MINUTES": "240",
            },
        ):
            test_settings = Settings()
            assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
            assert test_settings.REFRESH_TOKEN_EXPIRE_DAYS == 14
            assert test_settings.AGENT_TOKEN_EXPIRE_MINUTES == 240


class TestWebhookSecuritySettings:
    """Test webhook security configuration"""

    def test_google_calendar_webhook_token_optional(self):
        """GOOGLE_CALENDAR_WEBHOOK_TOKEN is optional"""
        test_settings = Settings()
        assert test_settings.GOOGLE_CALENDAR_WEBHOOK_TOKEN is None or isinstance(
            test_settings.GOOGLE_CALENDAR_WEBHOOK_TOKEN, str
        )

    def test_ii_agent_webhook_secret_optional(self):
        """II_AGENT_WEBHOOK_SECRET is optional"""
        test_settings = Settings()
        assert test_settings.II_AGENT_WEBHOOK_SECRET is None or isinstance(
            test_settings.II_AGENT_WEBHOOK_SECRET, str
        )

    def test_linear_webhook_secret_optional(self):
        """LINEAR_WEBHOOK_SECRET is optional"""
        test_settings = Settings()
        assert test_settings.LINEAR_WEBHOOK_SECRET is None or isinstance(
            test_settings.LINEAR_WEBHOOK_SECRET, str
        )

    def test_stripe_webhook_secret_optional(self):
        """STRIPE_WEBHOOK_SECRET is optional"""
        test_settings = Settings()
        assert test_settings.STRIPE_WEBHOOK_SECRET is None or isinstance(
            test_settings.STRIPE_WEBHOOK_SECRET, str
        )
