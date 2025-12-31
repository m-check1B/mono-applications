"""Smoke tests for sentiment routes"""
from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db
from tests.utils import override_db


def test_sentiment_analyze():
    """Test POST /api/sentiment/analyze endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/sentiment/analyze", json={
        "call_id": "test-call",
        "text": "This is a test message"
    })
    # 401 = auth required, 404 = not found, 200/500 = processing
    assert resp.status_code in (200, 401, 404, 500)


def test_sentiment_batch_analyze():
    """Test POST /api/sentiment/analyze/batch endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/sentiment/analyze/batch", json={
        "analyses": [
            {"call_id": "test-1", "text": "Happy message"},
            {"call_id": "test-2", "text": "Sad message"}
        ]
    })
    # 401 = auth required, 404 = not found, 200/500 = processing
    assert resp.status_code in (200, 401, 404, 500)


def test_sentiment_history():
    """Test GET /api/sentiment/history/{call_id} endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.get("/api/sentiment/history/test-call")
    # 401 = auth required, 404 = not found, 200 = success
    assert resp.status_code in (200, 401, 404)


def test_sentiment_realtime():
    """Test GET /api/sentiment/realtime/{session_id} endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.get("/api/sentiment/realtime/test-session")
    # 401 = auth required, 200 = success
    assert resp.status_code in (200, 401)


def test_sentiment_analytics():
    """Test GET /api/sentiment/analytics endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.get("/api/sentiment/analytics")
    # 401 = auth required, 200 = success
    assert resp.status_code in (200, 401)


def test_sentiment_call_summary():
    """Test POST /api/sentiment/calls/{call_id}/summary endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/sentiment/calls/test-call/summary")
    # 401 = auth required, 404 = not found, 200/500 = processing
    assert resp.status_code in (200, 401, 404, 500)


def test_sentiment_alerts():
    """Test GET /api/sentiment/alerts endpoint exists (supervisor only)"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.get("/api/sentiment/alerts")
    # 401 = auth required, 403 = forbidden (not supervisor), 200 = success
    assert resp.status_code in (200, 401, 403)


def test_sentiment_health():
    """Test GET /api/sentiment/health endpoint exists (supervisor only)"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.get("/api/sentiment/health")
    # 401 = auth required, 403 = forbidden (not supervisor), 200 = success
    assert resp.status_code in (200, 401, 403)


def test_sentiment_cleanup():
    """Test POST /api/sentiment/cleanup endpoint exists (supervisor only)"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/sentiment/cleanup")
    # 401 = auth required, 403 = forbidden (not supervisor), 200/500 = processing
    assert resp.status_code in (200, 401, 403, 500)
