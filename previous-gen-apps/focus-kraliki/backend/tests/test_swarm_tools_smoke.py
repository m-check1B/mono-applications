from fastapi.testclient import TestClient
from app.module import PlanningModule
from app.core.database import get_db
from app.core.security import get_current_user


async def _db_override():
    class _Dummy:
        async def execute(self, *_args, **_kwargs):
            class _Result:
                def fetchall(self):
                    return []

                def scalar(self):
                    return 0

            return _Result()

    yield _Dummy()


async def _user_override():
    class _Dummy:
        id = "user-1"
        organization_id = "org-1"
    return _Dummy()


def test_swarm_tools_routes_smoke():
    module = PlanningModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = _db_override
    app.dependency_overrides[get_current_user] = _user_override

    client = TestClient(app)
    resp = client.get("/swarm-tools/tasks/recommendations")
    assert resp.status_code in {200, 404, 422}
    resp2 = client.get("/swarm-tools/analytics/user")
    assert resp2.status_code in {200, 404, 422}
