"""Test enhanced module metrics tracking"""
from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db
from tests.utils import override_db


def test_module_metrics_comprehensive():
    """Test enhanced /metrics endpoint with route tracking"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    # Make several requests to different routes
    client.get("/api/calls/")
    client.get("/api/campaigns/")
    client.get("/api/analytics/dashboard")

    # Check metrics
    resp = client.get("/metrics")
    assert resp.status_code == 200

    body = resp.json()
    assert "module" in body
    assert body["module"] == "communications"
    assert "requests_total" in body
    assert body["requests_total"] >= 4  # At least 4 requests made
    assert "errors_total" in body
    assert "error_rate_percent" in body
    assert "status_codes" in body
    assert "top_routes" in body
    assert "routes_tracked" in body

    # Verify route tracking
    assert isinstance(body["top_routes"], list)
    if len(body["top_routes"]) > 0:
        route = body["top_routes"][0]
        assert "path" in route
        assert "count" in route
        assert "errors" in route
        assert "avg_duration_ms" in route


def test_module_metrics_status_codes():
    """Test status code tracking in metrics"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    # Make requests to various endpoints
    client.get("/api/calls/")
    client.get("/api/campaigns/")
    client.get("/api/nonexistent/route")

    # Check metrics
    resp = client.get("/metrics")
    assert resp.status_code == 200

    body = resp.json()
    status_codes = body["status_codes"]
    # Should have at least one status code tracked
    assert len(status_codes) > 0
    # Convert keys to int if they're strings, then check for common status codes
    status_keys = [int(k) if isinstance(k, str) else k for k in status_codes.keys()]
    has_common_status = any(code in status_keys for code in [200, 401, 404])
    assert has_common_status


def test_module_metrics_error_rate():
    """Test error rate calculation in metrics"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    # Make some requests
    client.get("/api/calls/")
    client.get("/api/campaigns/")

    # Check metrics
    resp = client.get("/metrics")
    assert resp.status_code == 200

    body = resp.json()
    assert body["error_rate_percent"] >= 0
    assert body["error_rate_percent"] <= 100


def test_module_metrics_route_duration():
    """Test route duration tracking"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    # Make request
    client.get("/api/calls/")

    # Check metrics
    resp = client.get("/metrics")
    assert resp.status_code == 200

    body = resp.json()
    if len(body["top_routes"]) > 0:
        route = body["top_routes"][0]
        assert route["avg_duration_ms"] >= 0
        assert isinstance(route["avg_duration_ms"], (int, float))
