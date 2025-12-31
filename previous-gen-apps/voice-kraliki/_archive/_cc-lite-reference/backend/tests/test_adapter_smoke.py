from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db


async def _override_db():
    class _Dummy:
        async def execute(self, *_args, **_kwargs):
            return object()

    yield _Dummy()


def test_platform_adapter_health_smoke():
    module = CommsModule(platform_mode=True)
    app = module.get_app()

    # Override DB dependency for health check
    app.dependency_overrides[get_db] = _override_db

    client = TestClient(app)
    # Platform mode requires platform headers
    headers = {
        "X-User-Id": "test-user-123",
        "X-Org-Id": "test-org-456",
        "X-User-Role": "admin"
    }
    resp = client.get("/api/metrics/health", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data


def test_agents_list_and_available_count_with_db_override():
    module = CommsModule(platform_mode=False)
    app = module.get_app()

    async def _db_override():
        class _Dummy:
            async def execute(self, *_args, **_kwargs):
                class _Result:
                    def scalars(self):
                        class _Scalars:
                            def all(self):
                                return []
                        return _Scalars()

                    def scalar(self):
                        return 0
                return _Result()
        yield _Dummy()

    app.dependency_overrides[get_db] = _db_override
    client = TestClient(app)
    assert client.get("/api/agents/").status_code == 200
    resp = client.get("/api/agents/available/count")
    assert resp.status_code == 200
    assert "available_agents" in resp.json()


def test_module_metrics_counts():
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    client = TestClient(app)
    client.get("/api/metrics/health")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["requests_total"] >= 1
