"""
Unit tests for Main Module
Tests app initialization, root endpoints, and health checks
"""

import pytest
from unittest.mock import patch, MagicMock


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_endpoint_returns_app_info(self, client):
        """Root endpoint returns app information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        # Check for expected fields (exact name may vary between Focus by Kraliki and Planning Module)
        assert "name" in data or "title" in data
        assert "version" in data
        assert "status" in data


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_endpoint(self, client):
        """Health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAppConfiguration:
    """Tests for app configuration"""

    def test_app_has_routes(self, app):
        """App has routes configured"""
        routes = list(app.routes)
        assert len(routes) > 0

    def test_routers_included(self, app):
        """Essential routers are included"""
        routes = [route.path for route in app.routes]

        # Check key routes exist
        expected_prefixes = [
            "/auth",
            "/tasks",
            "/billing",
            "/health"
        ]

        for prefix in expected_prefixes:
            has_route = any(prefix in route for route in routes)
            assert has_route, f"Missing route prefix: {prefix}"


class TestRouterIntegration:
    """Tests for router integration - basic unauthenticated tests"""

    def test_auth_router_mounted(self, client):
        """Auth router is accessible"""
        # Should return 422 for missing body, not 404
        response = client.post("/auth/login")
        assert response.status_code in [422, 400]  # Validation error or bad request

    def test_billing_router_mounted(self, client):
        """Billing router is accessible (unauthenticated)"""
        response = client.get("/billing/plans")
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling - basic tests"""

    def test_404_for_unknown_route(self, client):
        """Unknown routes return 404"""
        response = client.get("/nonexistent/route/definitely/not/exists")
        assert response.status_code == 404


class TestSecurityHeaders:
    """Tests for OWASP security headers middleware (VD-404)"""

    def test_x_content_type_options_header(self, client):
        """X-Content-Type-Options header prevents MIME sniffing"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options_header(self, client):
        """X-Frame-Options header prevents clickjacking"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("x-frame-options") == "SAMEORIGIN"

    def test_x_xss_protection_header(self, client):
        """X-XSS-Protection header enables browser XSS filter"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("x-xss-protection") == "1; mode=block"

    def test_referrer_policy_header(self, client):
        """Referrer-Policy header controls referrer information"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    def test_permissions_policy_header(self, client):
        """Permissions-Policy header restricts browser features"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("permissions-policy") == "geolocation=(), microphone=(), camera=()"

    def test_content_security_policy_header(self, client):
        """Content-Security-Policy header controls resource loading"""
        response = client.get("/health")
        assert response.status_code == 200
        csp = response.headers.get("content-security-policy")
        assert csp is not None
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'self'" in csp

    def test_security_headers_on_api_endpoint(self, client):
        """Security headers present on API endpoints too"""
        response = client.get("/billing/plans")
        assert response.status_code == 200
        # All security headers should be present
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "SAMEORIGIN"
        assert response.headers.get("x-xss-protection") == "1; mode=block"
        assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    def test_security_headers_on_post_request(self, client):
        """Security headers present on POST responses"""
        response = client.post("/auth/login")
        # Should be 422 (validation error) but headers should still be present
        assert response.status_code in [400, 422]
        assert response.headers.get("x-content-type-options") == "nosniff"

    def test_security_headers_on_error_response(self, client):
        """Security headers present even on 404 responses"""
        response = client.get("/nonexistent-route")
        assert response.status_code == 404
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "SAMEORIGIN"

    def test_strict_transport_security_header(self, client):
        """Strict-Transport-Security (HSTS) header enforces HTTPS"""
        response = client.get("/health")
        assert response.status_code == 200
        hsts = response.headers.get("strict-transport-security")
        assert hsts is not None
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts
