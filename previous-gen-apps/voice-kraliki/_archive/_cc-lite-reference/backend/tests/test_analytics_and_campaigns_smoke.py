from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db
from app.dependencies import get_current_user
from .utils import DummyAsyncDB


class _DummyUser:
    def __init__(self):
        self.id = "user-1"
        self.organization_id = "org-1"
        # Use string role to avoid importing enums here
        self.role = type("Role", (), {"value": "admin"})()


async def _db_dummy():
    yield DummyAsyncDB()


async def _user_dummy():
    return _DummyUser()


def _mk_app():
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = _db_dummy
    app.dependency_overrides[get_current_user] = _user_dummy
    return app


def test_campaigns_list_smoke():
    app = _mk_app()
    client = TestClient(app)
    resp = client.get("/api/campaigns/?skip=0&limit=10")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_analytics_dashboard_smoke():
    app = _mk_app()
    client = TestClient(app)
    resp = client.get("/api/analytics/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    # Check for actual dashboard metrics
    assert "total_calls_24h" in data
    assert "active_calls" in data
    assert "active_campaigns" in data


def test_analytics_calls_grouped_smoke():
    app = _mk_app()
    client = TestClient(app)
    resp = client.get("/api/analytics/calls?group_by=day")
    assert resp.status_code == 200
    body = resp.json()
    assert "summary" in body and "metrics" in body
