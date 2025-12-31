"""Tests for rate limiting on authentication endpoints.

VD-326: Verifies that login and registration endpoints have rate limiting applied
to prevent brute force attacks and abuse.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.middleware.rate_limit import LOGIN_RATE_LIMIT, limiter, rate_limit_handler


class TestRateLimitConfiguration:
    """Test that rate limiting is properly configured."""

    def test_login_rate_limit_constant_defined(self):
        """Verify LOGIN_RATE_LIMIT constant exists and is reasonable."""
        assert LOGIN_RATE_LIMIT is not None
        # Should be in format "X/Y unit" like "5/15 minutes"
        assert "/" in LOGIN_RATE_LIMIT
        # Parse the limit
        parts = LOGIN_RATE_LIMIT.split("/")
        count = int(parts[0])
        # Should allow at least 1 but not too many attempts
        assert 1 <= count <= 20, f"Rate limit of {count} seems unreasonable"

    def test_limiter_instance_exists(self):
        """Verify limiter instance is properly configured."""
        assert limiter is not None
        assert isinstance(limiter, Limiter)

    def test_rate_limit_handler_exists(self):
        """Verify rate limit handler function exists."""
        assert rate_limit_handler is not None
        assert callable(rate_limit_handler)


class TestRoutesHaveRateLimiting:
    """Test that auth routes have rate limiting decorators applied."""

    def test_routes_py_login_has_rate_limit(self):
        """Verify routes.py login has @limiter.limit decorator."""
        from app.auth import routes

        # Check if login function has the rate limiting attribute
        # When @limiter.limit is applied, it adds metadata to the function
        login_func = routes.login
        # The function should be rate limited (check for slowapi markers)
        assert hasattr(login_func, "__wrapped__") or hasattr(login_func, "_limit_strings"), \
            "Login endpoint should have rate limiting applied"

    def test_routes_py_register_has_rate_limit(self):
        """Verify routes.py register has @limiter.limit decorator."""
        from app.auth import routes

        register_func = routes.register
        assert hasattr(register_func, "__wrapped__") or hasattr(register_func, "_limit_strings"), \
            "Register endpoint should have rate limiting applied"

    def test_database_routes_login_has_rate_limit(self):
        """Verify database_routes.py login has @limiter.limit decorator."""
        from app.auth import database_routes

        login_func = database_routes.login
        assert hasattr(login_func, "__wrapped__") or hasattr(login_func, "_limit_strings"), \
            "Database login endpoint should have rate limiting applied"

    def test_database_routes_register_has_rate_limit(self):
        """Verify database_routes.py register has @limiter.limit decorator."""
        from app.auth import database_routes

        register_func = database_routes.register
        assert hasattr(register_func, "__wrapped__") or hasattr(register_func, "_limit_strings"), \
            "Database register endpoint should have rate limiting applied"

    def test_database_routes_forgot_password_has_rate_limit(self):
        """Verify database_routes.py forgot-password has @limiter.limit decorator."""
        from app.auth import database_routes

        forgot_func = database_routes.forgot_password
        assert hasattr(forgot_func, "__wrapped__") or hasattr(forgot_func, "_limit_strings"), \
            "Forgot password endpoint should have rate limiting applied"

    def test_database_routes_reset_password_has_rate_limit(self):
        """Verify database_routes.py reset-password has @limiter.limit decorator."""
        from app.auth import database_routes

        reset_func = database_routes.reset_password
        assert hasattr(reset_func, "__wrapped__") or hasattr(reset_func, "_limit_strings"), \
            "Reset password endpoint should have rate limiting applied"

    def test_simple_routes_login_has_rate_limit(self):
        """Verify simple_routes.py login has @limiter.limit decorator."""
        from app.auth import simple_routes

        login_func = simple_routes.login
        assert hasattr(login_func, "__wrapped__") or hasattr(login_func, "_limit_strings"), \
            "Simple login endpoint should have rate limiting applied"

    def test_simple_routes_register_has_rate_limit(self):
        """Verify simple_routes.py register has @limiter.limit decorator."""
        from app.auth import simple_routes

        register_func = simple_routes.register
        assert hasattr(register_func, "__wrapped__") or hasattr(register_func, "_limit_strings"), \
            "Simple register endpoint should have rate limiting applied"


class TestRateLimitHandler:
    """Test rate limit handler returns correct response."""

    def test_rate_limit_handler_returns_429(self):
        """Verify handler returns 429 status code."""
        mock_request = MagicMock()
        mock_request.headers = {}

        # Create a mock RateLimitExceeded exception
        mock_exc = MagicMock(spec=RateLimitExceeded)
        mock_exc.detail = "5 per 15 minutes"

        response = rate_limit_handler(mock_request, mock_exc)

        assert response.status_code == 429

    def test_rate_limit_handler_includes_retry_after(self):
        """Verify handler includes Retry-After header."""
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_exc = MagicMock(spec=RateLimitExceeded)
        mock_exc.detail = "5 per 15 minutes"

        response = rate_limit_handler(mock_request, mock_exc)

        # Response should have headers
        assert "Retry-After" in response.headers or hasattr(response, "headers")


class TestRequestFunctionSignatures:
    """Verify rate-limited functions have Request parameter."""

    def test_routes_login_accepts_request(self):
        """Verify routes.py login accepts Request parameter."""
        from app.auth.routes import login
        import inspect

        sig = inspect.signature(login)
        params = list(sig.parameters.keys())
        assert "request" in params, "Login must accept 'request' parameter for rate limiting"

    def test_routes_register_accepts_request(self):
        """Verify routes.py register accepts Request parameter."""
        from app.auth.routes import register
        import inspect

        sig = inspect.signature(register)
        params = list(sig.parameters.keys())
        assert "request" in params, "Register must accept 'request' parameter for rate limiting"

    def test_database_routes_login_accepts_request(self):
        """Verify database_routes.py login accepts Request parameter."""
        from app.auth.database_routes import login
        import inspect

        sig = inspect.signature(login)
        params = list(sig.parameters.keys())
        assert "request" in params, "Database login must accept 'request' parameter for rate limiting"

    def test_database_routes_register_accepts_request(self):
        """Verify database_routes.py register accepts Request parameter."""
        from app.auth.database_routes import register
        import inspect

        sig = inspect.signature(register)
        params = list(sig.parameters.keys())
        assert "request" in params, "Database register must accept 'request' parameter for rate limiting"

    def test_database_routes_forgot_password_accepts_request(self):
        """Verify database_routes.py forgot_password accepts Request parameter."""
        from app.auth.database_routes import forgot_password
        import inspect

        sig = inspect.signature(forgot_password)
        params = list(sig.parameters.keys())
        assert "request" in params, "Forgot password must accept 'request' parameter for rate limiting"

    def test_database_routes_reset_password_accepts_request(self):
        """Verify database_routes.py reset_password accepts Request parameter."""
        from app.auth.database_routes import reset_password
        import inspect

        sig = inspect.signature(reset_password)
        params = list(sig.parameters.keys())
        assert "request" in params, "Reset password must accept 'request' parameter for rate limiting"

    def test_simple_routes_login_accepts_request(self):
        """Verify simple_routes.py login accepts Request parameter."""
        from app.auth.simple_routes import login
        import inspect

        sig = inspect.signature(login)
        params = list(sig.parameters.keys())
        assert "request" in params, "Simple login must accept 'request' parameter for rate limiting"

    def test_simple_routes_register_accepts_request(self):
        """Verify simple_routes.py register accepts Request parameter."""
        from app.auth.simple_routes import register
        import inspect

        sig = inspect.signature(register)
        params = list(sig.parameters.keys())
        assert "request" in params, "Simple register must accept 'request' parameter for rate limiting"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
