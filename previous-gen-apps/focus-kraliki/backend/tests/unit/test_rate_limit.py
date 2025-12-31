"""
Unit tests for Rate Limiting middleware
Tests client IP extraction and rate limit decorators
"""

import pytest
from unittest.mock import MagicMock

from app.middleware.rate_limit import (
    get_client_ip,
    auth_rate_limit,
    ai_rate_limit,
    general_rate_limit,
    webhook_rate_limit,
)


class TestGetClientIP:
    """Test client IP extraction from requests"""

    def test_ip_from_x_forwarded_for(self):
        """Extracts IP from X-Forwarded-For header"""
        mock_request = MagicMock()
        mock_request.headers.get.side_effect = lambda h: {
            "X-Forwarded-For": "203.0.113.195, 70.41.3.18",
            "X-Real-IP": None,
        }.get(h)
        mock_request.client.host = "127.0.0.1"

        ip = get_client_ip(mock_request)
        assert ip == "203.0.113.195"

    def test_ip_from_x_forwarded_for_single(self):
        """Handles single IP in X-Forwarded-For"""
        mock_request = MagicMock()
        mock_request.headers.get.side_effect = lambda h: {
            "X-Forwarded-For": "192.168.1.100",
            "X-Real-IP": None,
        }.get(h)
        mock_request.client.host = "127.0.0.1"

        ip = get_client_ip(mock_request)
        assert ip == "192.168.1.100"

    def test_ip_from_x_real_ip(self):
        """Falls back to X-Real-IP header"""
        mock_request = MagicMock()
        mock_request.headers.get.side_effect = lambda h: {
            "X-Forwarded-For": None,
            "X-Real-IP": "10.0.0.50",
        }.get(h)
        mock_request.client.host = "127.0.0.1"

        ip = get_client_ip(mock_request)
        assert ip == "10.0.0.50"

    def test_ip_from_client_host(self):
        """Falls back to request.client.host"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.client.host = "192.168.0.1"

        ip = get_client_ip(mock_request)
        assert ip == "192.168.0.1"

    def test_ip_unknown_when_no_client(self):
        """Returns 'unknown' when client is None"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.client = None

        ip = get_client_ip(mock_request)
        assert ip == "unknown"

    def test_ip_strips_whitespace(self):
        """Strips whitespace from forwarded IPs"""
        mock_request = MagicMock()
        mock_request.headers.get.side_effect = lambda h: {
            "X-Forwarded-For": "  192.168.1.1  , 10.0.0.1",
            "X-Real-IP": None,
        }.get(h)
        mock_request.client.host = "127.0.0.1"

        ip = get_client_ip(mock_request)
        assert ip == "192.168.1.1"

    def test_ip_priority_forwarded_over_real(self):
        """X-Forwarded-For takes priority over X-Real-IP"""
        mock_request = MagicMock()
        mock_request.headers.get.side_effect = lambda h: {
            "X-Forwarded-For": "1.2.3.4",
            "X-Real-IP": "5.6.7.8",
        }.get(h)
        mock_request.client.host = "127.0.0.1"

        ip = get_client_ip(mock_request)
        assert ip == "1.2.3.4"


class TestRateLimitDecorators:
    """Test rate limit decorator factories"""

    def test_auth_rate_limit_returns_decorator(self):
        """auth_rate_limit returns a decorator"""
        decorator = auth_rate_limit(max_requests=5, window_seconds=300)
        assert callable(decorator)

    def test_ai_rate_limit_returns_decorator(self):
        """ai_rate_limit returns a decorator"""
        decorator = ai_rate_limit(max_requests=50, window_seconds=3600)
        assert callable(decorator)

    def test_general_rate_limit_returns_decorator(self):
        """general_rate_limit returns a decorator"""
        decorator = general_rate_limit(max_requests=1000, window_seconds=3600)
        assert callable(decorator)

    def test_auth_rate_limit_default_values(self):
        """auth_rate_limit has sensible defaults"""
        decorator = auth_rate_limit()
        assert callable(decorator)

    def test_ai_rate_limit_default_values(self):
        """ai_rate_limit has sensible defaults"""
        decorator = ai_rate_limit()
        assert callable(decorator)

    def test_general_rate_limit_default_values(self):
        """general_rate_limit has sensible defaults"""
        decorator = general_rate_limit()
        assert callable(decorator)

    def test_webhook_rate_limit_returns_decorator(self):
        """webhook_rate_limit returns a decorator"""
        decorator = webhook_rate_limit(max_requests=30, window_seconds=60)
        assert callable(decorator)

    def test_webhook_rate_limit_default_values(self):
        """webhook_rate_limit has sensible defaults"""
        decorator = webhook_rate_limit()
        assert callable(decorator)
