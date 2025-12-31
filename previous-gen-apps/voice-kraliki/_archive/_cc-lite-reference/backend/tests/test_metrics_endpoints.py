from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db


async def _override_db():
    class _Dummy:
        async def execute(self, *_args, **_kwargs):
            class _R:
                def scalar(self):
                    return 0
            return _R()

    yield _Dummy()


def test_metrics_system():
    """Test /api/metrics/system endpoint exists (requires auth)"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    client = TestClient(app)
    resp = client.get("/api/metrics/system")
    # 401 = auth required, 200 = success
    assert resp.status_code in (200, 401)


def test_metrics_application_with_db_override():
    """Test /api/metrics/application endpoint exists (requires auth)"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = _override_db
    client = TestClient(app)
    resp = client.get("/api/metrics/application")
    # 401 = auth required, 200 = success
    assert resp.status_code in (200, 401)
