from fastapi.testclient import TestClient
from app.module import PlanningModule
from app.core.database import get_db
from app.core.security import get_current_user


class DummyQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *args, **kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def count(self):
        return len(self.items)

    def all(self):
        return self.items

    def first(self):
        return self.items[0] if self.items else None

    def order_by(self, *_args, **_kwargs):
        return self


class DummyDB:
    def __init__(self):
        self.projects = []
        self.tasks = []

    def query(self, model):
        name = getattr(model, "__name__", "")
        if name == "Project":
            return DummyQuery(self.projects)
        if name == "Task":
            return DummyQuery(self.tasks)
        return DummyQuery([])

    def commit(self):
        return None

    def refresh(self, _obj):
        return None

    def add(self, _obj):
        return None


async def _db_override():
    yield DummyDB()


async def _user_override():
    class DummyUser:
        id = "user-1"
        organization_id = "org-1"

    return DummyUser()


def _mk_client():
    module = PlanningModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = _db_override
    app.dependency_overrides[get_current_user] = _user_override
    return TestClient(app)


def test_projects_list_smoke():
    client = _mk_client()
    resp = client.get("/projects/")
    assert resp.status_code == 200


def test_ai_scheduler_recommendations_smoke():
    client = _mk_client()
    resp = client.get("/ai-scheduler/tasks/prioritize")
    assert resp.status_code in {200, 404}
