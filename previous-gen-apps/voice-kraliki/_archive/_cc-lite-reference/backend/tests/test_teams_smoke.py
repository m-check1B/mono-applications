from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db
from app.dependencies import get_current_user


class _DummyUser:
    def __init__(self):
        self.id = "user-1"
        self.organization_id = "org-1"
        self.role = type("Role", (), {"value": "admin"})()


async def _db_override():
    class _Dummy:
        async def execute(self, *_args, **_kwargs):
            class _Result:
                def fetchall(self):
                    return []

                def scalar(self):
                    return 0

                def scalars(self):
                    class _Scalars:
                        def all(self):
                            return []

                    return _Scalars()

            return _Result()

    yield _Dummy()


async def _user_override():
    return _DummyUser()


def test_teams_routes_smoke():
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = _db_override
    app.dependency_overrides[get_current_user] = _user_override
    client = TestClient(app)

    assert client.get("/api/teams/").status_code == 200
    assert client.get("/api/teams/available/summary").status_code in {200, 404}
