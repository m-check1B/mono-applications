"""Tests for configuration validation.

Security: Ensures misconfigurations are caught at startup to prevent
insecure deployments.
"""

import pytest
from pydantic import ValidationError


class TestWebhookSecretValidation:
    """Tests for webhook secret validation in Settings."""

    def test_settings_rejects_webhook_url_without_secret(self):
        """Settings should reject webhook URL without a secret (fail fast)."""
        from app.core.config import Settings

        with pytest.raises(ValidationError) as exc_info:
            Settings(
                telegram_webhook_url="https://example.com",
                telegram_webhook_secret=""
            )

        error_msg = str(exc_info.value)
        assert "TELEGRAM_WEBHOOK_SECRET is required" in error_msg

    def test_settings_rejects_whitespace_only_secret(self):
        """Settings should reject whitespace-only secret (security edge case)."""
        from app.core.config import Settings

        with pytest.raises(ValidationError) as exc_info:
            Settings(
                telegram_webhook_url="https://example.com",
                telegram_webhook_secret="   "
            )

        error_msg = str(exc_info.value)
        assert "TELEGRAM_WEBHOOK_SECRET is required" in error_msg

    def test_settings_accepts_valid_webhook_config(self):
        """Settings should accept valid webhook URL + secret pair."""
        from app.core.config import Settings

        # Should not raise
        settings = Settings(
            telegram_webhook_url="https://example.com",
            telegram_webhook_secret="secure-random-secret-123"
        )

        assert settings.telegram_webhook_url == "https://example.com"
        assert settings.telegram_webhook_secret == "secure-random-secret-123"

    def test_settings_allows_no_webhook_mode(self):
        """Settings should allow no webhook URL (polling mode)."""
        from app.core.config import Settings

        # Should not raise - polling mode doesn't need secret
        settings = Settings(
            telegram_webhook_url="",
            telegram_webhook_secret=""
        )

        assert settings.telegram_webhook_url == ""
        assert settings.telegram_webhook_secret == ""

    def test_settings_allows_secret_without_webhook_url(self):
        """Settings should allow secret without webhook URL (pre-configured)."""
        from app.core.config import Settings

        # Should not raise - secret is set but not used yet
        settings = Settings(
            telegram_webhook_url="",
            telegram_webhook_secret="prepared-secret"
        )

        assert settings.telegram_webhook_secret == "prepared-secret"

    def test_error_message_includes_generation_hint(self):
        """Error message should include hint on how to generate a secret."""
        from app.core.config import Settings

        with pytest.raises(ValidationError) as exc_info:
            Settings(
                telegram_webhook_url="https://example.com",
                telegram_webhook_secret=""
            )

        error_msg = str(exc_info.value)
        assert "openssl rand" in error_msg or "random" in error_msg.lower()


class TestDockerSecurityConfiguration:
    """Tests for Docker security configuration.

    Security: Ensures .dockerignore prevents sensitive files from entering
    Docker build context, reducing risk of secret leakage.
    """

    def test_dockerignore_exists(self):
        """Project must have a .dockerignore file for security."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        dockerignore = project_root / ".dockerignore"

        assert dockerignore.exists(), (
            "Missing .dockerignore file! Docker build context may include "
            "sensitive files like .env, secrets, and Git history."
        )

    def test_dockerignore_excludes_env_files(self):
        """Ensure .dockerignore excludes .env files to prevent secret leakage."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        dockerignore = project_root / ".dockerignore"

        content = dockerignore.read_text()

        # Must exclude .env patterns
        assert ".env" in content, ".dockerignore must exclude .env files"

    def test_dockerignore_excludes_git_directory(self):
        """Ensure .dockerignore excludes .git to prevent history leakage."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        dockerignore = project_root / ".dockerignore"

        content = dockerignore.read_text()

        assert ".git" in content, ".dockerignore must exclude .git directory"

    def test_dockerignore_excludes_secrets_patterns(self):
        """Ensure .dockerignore excludes common secret file patterns."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        dockerignore = project_root / ".dockerignore"

        content = dockerignore.read_text()

        secret_patterns = ["*.pem", "*.key"]
        for pattern in secret_patterns:
            assert pattern in content, f".dockerignore must exclude {pattern}"

    def test_dockerignore_excludes_test_files(self):
        """Ensure .dockerignore excludes tests (not needed in production)."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        dockerignore = project_root / ".dockerignore"

        content = dockerignore.read_text()

        assert "tests/" in content or "tests" in content, (
            ".dockerignore should exclude tests directory"
        )

    def test_dockerignore_excludes_venv(self):
        """Ensure .dockerignore excludes virtual environment directories."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        dockerignore = project_root / ".dockerignore"

        content = dockerignore.read_text()

        # Must exclude venv patterns
        venv_patterns = [".venv", "venv"]
        found = any(p in content for p in venv_patterns)
        assert found, ".dockerignore must exclude virtual environment directories"

    def test_dockerignore_allows_entrypoint(self):
        """Ensure docker-entrypoint.sh is NOT excluded (needed for container)."""
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        dockerignore = project_root / ".dockerignore"

        content = dockerignore.read_text()

        # If *.sh is excluded, docker-entrypoint.sh must be explicitly allowed
        if "*.sh" in content:
            assert "!docker-entrypoint.sh" in content, (
                ".dockerignore excludes *.sh but must allow docker-entrypoint.sh"
            )
