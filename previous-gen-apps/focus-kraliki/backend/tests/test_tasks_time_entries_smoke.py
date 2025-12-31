from fastapi.testclient import TestClient
from app.module import PlanningModule
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.task import TaskResponse
from app.schemas.time_entry import TimeEntryResponse


class DummyUser:
    def __init__(self, user_id="user-1"):
        self.id = user_id
        self.organization_id = "org-1"


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

    def order_by(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.items[0] if self.items else None


class DummyDB:
    def __init__(self, tasks=None, entries=None):
        self.tasks = tasks or []
        self.entries = entries or []

    def query(self, model):
        if getattr(model, "__name__", "") == "Task":
            return DummyQuery(self.tasks)
        return DummyQuery(self.entries)

    def commit(self):
        return None

    def refresh(self, _obj):
        return None

    def add(self, _obj):
        return None


async def _db_override():
    yield DummyDB()


async def _user_override():
    return DummyUser()


def _mk_app(monkeypatch):
    module = PlanningModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = _db_override
    app.dependency_overrides[get_current_user] = _user_override

    def _task_validate(cls, obj, *_args, **_kwargs):
        return {"id": getattr(obj, "id", "task-1")}

    def _entry_validate(cls, obj, *_args, **_kwargs):
        return {"id": getattr(obj, "id", "entry-1")}

    monkeypatch.setattr(TaskResponse, "model_validate", classmethod(_task_validate))
    monkeypatch.setattr(TimeEntryResponse, "model_validate", classmethod(_entry_validate))
    return app


def test_tasks_list_smoke(monkeypatch):
    app = _mk_app(monkeypatch)
    client = TestClient(app)
    resp = client.get("/tasks/")
    assert resp.status_code == 200


def test_time_entries_list_smoke(monkeypatch):
    app = _mk_app(monkeypatch)
    client = TestClient(app)
    resp = client.get("/time-entries/")
    assert resp.status_code == 200
