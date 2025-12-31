from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db
from app.dependencies import get_current_user


class DummyUser:
    def __init__(self, role="admin"):
        self.id = "user-1"
        self.organization_id = "org-1"
        self.role = type("Role", (), {"value": role})()


async def _db_dummy():
    class _Dummy:
        async def execute(self, *_args, **_kwargs):
            class _R:
                def scalar(self):
                    return 0

                def scalars(self):
                    class _S:
                        def all(self):
                            return []

                    return _S()

                def fetchall(self):
                    return []

            return _R()

        async def commit(self):
            return None

        async def refresh(self, _obj):
            return None

        def add(self, _obj):
            return None

    yield _Dummy()


async def _user_dummy():
    return DummyUser()


def _mk_app(role="admin"):
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = _db_dummy
    async def _user():
        return DummyUser(role)
    app.dependency_overrides[get_current_user] = _user
    return app


def test_analytics_agent_performance_admin():
    app = _mk_app(role="admin")
    client = TestClient(app)
    resp = client.get("/api/analytics/agents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_analytics_agent_performance_agent_limit():
    app = _mk_app(role="agent")
    client = TestClient(app)
    resp = client.get("/api/analytics/agents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
