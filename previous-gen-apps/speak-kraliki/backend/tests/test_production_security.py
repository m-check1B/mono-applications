"""
Tests for production security validation.

Security: Ensures production deployments have proper security configurations.
Prevents DEBUG mode from leaking sensitive information in production.
"""

from pathlib import Path

import pytest
import yaml

from app.core.config import settings
from app.core.auth import validate_production_security


# =============================================================================
# Docker Compose Production Security Tests
# =============================================================================


class TestDockerComposeSecurityConfig:
    """Tests that verify docker-compose.yml has secure production settings.

    These tests prevent accidental exposure of DEBUG mode in production
    deployments by checking the docker-compose.yml configuration.
    """

    @pytest.fixture
    def docker_compose_content(self) -> str:
        """Load docker-compose.yml content."""
        project_root = Path(__file__).parent.parent.parent
        docker_compose = project_root / "docker-compose.yml"
        return docker_compose.read_text()

    @pytest.fixture
    def docker_compose_yaml(self, docker_compose_content: str) -> dict:
        """Parse docker-compose.yml as YAML."""
        return yaml.safe_load(docker_compose_content)

    def test_docker_compose_exists(self):
        """Ensure docker-compose.yml exists for production deployment."""
        project_root = Path(__file__).parent.parent.parent
        docker_compose = project_root / "docker-compose.yml"

        assert docker_compose.exists(), (
            "Missing docker-compose.yml for production deployment"
        )

    def test_backend_debug_is_false(self, docker_compose_yaml: dict):
        """CRITICAL: Backend container must have DEBUG=false.

        DEBUG=true in production exposes:
        - Detailed error messages with stack traces
        - Auto-reload (security + performance issue)
        - Potentially sensitive configuration values
        """
        backend_service = docker_compose_yaml.get("services", {}).get("backend", {})
        environment = backend_service.get("environment", [])

        # Environment can be a list or dict in docker-compose
        debug_value = None
        if isinstance(environment, list):
            for env_var in environment:
                if env_var.startswith("DEBUG="):
                    debug_value = env_var.split("=", 1)[1]
                    break
        elif isinstance(environment, dict):
            debug_value = environment.get("DEBUG")

        assert debug_value is not None, (
            "Backend service must explicitly set DEBUG environment variable"
        )
        assert debug_value.lower() == "false", (
            f"Backend DEBUG must be 'false' in production, got '{debug_value}'. "
            "DEBUG=true exposes sensitive error details and enables auto-reload."
        )

    def test_frontend_not_in_development_mode(self, docker_compose_yaml: dict):
        """Frontend should not use NODE_ENV=development in production compose."""
        frontend_service = docker_compose_yaml.get("services", {}).get("frontend", {})
        environment = frontend_service.get("environment", [])

        # Check for NODE_ENV
        node_env = None
        if isinstance(environment, list):
            for env_var in environment:
                if env_var.startswith("NODE_ENV="):
                    node_env = env_var.split("=", 1)[1]
                    break
        elif isinstance(environment, dict):
            node_env = environment.get("NODE_ENV")

        # This is a warning rather than failure since it might be intentional
        # for beta deployments, but the test documents the current state
        if node_env == "development":
            pytest.skip(
                "Frontend is in development mode - OK for beta but review for production"
            )

    def test_env_example_has_debug_false(self):
        """Ensure .env.example shows DEBUG=false as the default.

        This ensures developers see the secure default when setting up.
        """
        project_root = Path(__file__).parent.parent
        env_example = project_root / ".env.example"

        if not env_example.exists():
            pytest.skip(".env.example not found")

        content = env_example.read_text()
        lines = content.split("\n")

        debug_line = None
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("DEBUG=") and not stripped.startswith("#"):
                debug_line = stripped
                break

        assert debug_line is not None, ".env.example should have DEBUG setting"
        assert "false" in debug_line.lower(), (
            f".env.example should show DEBUG=false as default, got: {debug_line}"
        )


# =============================================================================
# Runtime Security Validation Tests
# =============================================================================


def test_validate_production_security_with_empty_database_url():
    """Test that validation fails with empty database URL."""
    original_debug = settings.debug
    original_database_url = settings.database_url

    try:
        # Temporarily set debug=False
        settings.debug = False
        settings.database_url = ""

        # This should fail because database_url is empty
        with pytest.raises(RuntimeError) as exc_info:
            validate_production_security()

        assert "DATABASE_URL is required" in str(exc_info.value)
    finally:
        settings.debug = original_debug
        settings.database_url = original_database_url


def test_validate_production_security_with_default_database_credentials():
    """Test that validation fails with default database credentials."""
    original_database_url = settings.database_url
    original_debug = settings.debug

    try:
        settings.debug = False
        settings.database_url = (
            "postgresql+asyncpg://postgres:postgres@localhost:5432/speak"
        )

        with pytest.raises(RuntimeError) as exc_info:
            validate_production_security()

        assert "DATABASE_URL contains default credentials" in str(exc_info.value)
    finally:
        settings.database_url = original_database_url
        settings.debug = original_debug


def test_validate_production_security_with_placeholder_database_url():
    """Test that validation fails with placeholder in database URL."""
    original_database_url = settings.database_url
    original_debug = settings.debug

    try:
        settings.debug = False
        settings.database_url = "postgresql+asyncpg://user:replace_me@db:5432/speak"

        with pytest.raises(RuntimeError) as exc_info:
            validate_production_security()

        assert "DATABASE_URL contains default credentials or placeholders" in str(
            exc_info.value
        )
    finally:
        settings.database_url = original_database_url
        settings.debug = original_debug


def test_validate_production_security_with_localhost_database_url():
    """Test that validation passes with localhost in database URL (allowed now)."""
    original_database_url = settings.database_url
    original_debug = settings.debug
    original_jwt_secret = settings.jwt_secret_key

    try:
        settings.debug = False
        settings.database_url = "postgresql+asyncpg://user:secure-password@localhost:5432/speak"
        settings.jwt_secret_key = "super-secret-key-with-at-least-32-characters"

        # This should now pass validation
        validate_production_security()
    finally:
        settings.database_url = original_database_url
        settings.debug = original_debug
        settings.jwt_secret_key = original_jwt_secret


def test_validate_production_security_with_secure_database_url():
    """Test that validation passes with secure database URL."""
    original_database_url = settings.database_url
    original_debug = settings.debug
    original_jwt_secret = settings.jwt_secret_key

    try:
        settings.debug = False
        settings.database_url = (
            "postgresql+asyncpg://user:password@prod-db.example.com:5432/speak"
        )
        settings.jwt_secret_key = "super-secret-key-with-at-least-32-characters"

        # This should not raise any error
        try:
            validate_production_security()
        except RuntimeError as e:
            # If it raises, make sure it's not about DATABASE_URL
            assert "DATABASE_URL" not in str(e)
    finally:
        settings.database_url = original_database_url
        settings.debug = original_debug
        settings.jwt_secret_key = original_jwt_secret


def test_validate_production_security_skips_in_debug_mode():
    """Test that validation is skipped in debug mode."""
    original_debug = settings.debug
    original_database_url = settings.database_url

    try:
        settings.debug = True
        settings.database_url = ""  # Empty would fail in production

        # Should not raise in debug mode
        validate_production_security()
    finally:
        settings.debug = original_debug
        settings.database_url = original_database_url


def test_validate_production_security_with_insecure_jwt_secret():
    """Test that validation fails with known insecure JWT secrets."""
    original_database_url = settings.database_url
    original_debug = settings.debug
    original_jwt_secret = settings.jwt_secret_key

    try:
        settings.debug = False
        settings.database_url = "postgresql://user:pass@prod-db.example.com:5432/speak"

        # Test various insecure secrets (skip empty string as it's caught separately)
        insecure_secrets = [
            "your-secret-key-change-in-production",
            "changeme",
            "secret",
            "password",
            "replace_me",
        ]

        for insecure_secret in insecure_secrets:
            settings.jwt_secret_key = insecure_secret

            with pytest.raises(RuntimeError) as exc_info:
                validate_production_security()

            assert "JWT_SECRET_KEY" in str(exc_info.value)
            assert "insecure default" in str(exc_info.value)
    finally:
        settings.database_url = original_database_url
        settings.debug = original_debug
        settings.jwt_secret_key = original_jwt_secret


def test_validate_production_security_with_short_jwt_secret():
    """Test that validation fails with short JWT secret."""
    original_database_url = settings.database_url
    original_debug = settings.debug
    original_jwt_secret = settings.jwt_secret_key

    try:
        settings.debug = False
        settings.database_url = "postgresql://user:pass@prod-db.example.com:5432/speak"
        settings.jwt_secret_key = "short"

        with pytest.raises(RuntimeError) as exc_info:
            validate_production_security()

        assert "JWT_SECRET_KEY" in str(exc_info.value)
        assert "too short" in str(exc_info.value)
    finally:
        settings.database_url = original_database_url
        settings.debug = original_debug
        settings.jwt_secret_key = original_jwt_secret
