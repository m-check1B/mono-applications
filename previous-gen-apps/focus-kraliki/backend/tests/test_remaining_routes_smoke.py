"""
Smoke tests for remaining routes (Phase 2 observability)
- auth_v2
- users
- assistant
- google_oauth
- pricing
- integration_calendar
- shadow
- ai
"""
from fastapi.testclient import TestClient
from app.module import PlanningModule
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.token_revocation import token_blacklist
from datetime import datetime


class DummyUser:
    def __init__(self, user_id="user-1", org_id="org-1"):
        from app.models.user import Role, UserStatus
        self.id = user_id
        self.organization_id = org_id
        self.email = "test@example.com"
        self.full_name = "Test User"
        self.username = "testuser"
        self.firstName = "Test"
        self.lastName = "User"
        self.preferences = {}
        self.role = Role.AGENT
        self.status = UserStatus.ACTIVE
        self.createdAt = datetime.utcnow()


class DummyQuery:
    def __init__(self, items=None):
        self.items = items or []

    def filter(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def offset(self, *args, **kwargs):
        return self

    def count(self):
        return len(self.items)

    def all(self):
        return self.items

    def first(self):
        return self.items[0] if self.items else None

    def order_by(self, *args, **kwargs):
        return self


class DummyDB:
    def __init__(self):
        self.users = []
        self.tasks = []
        self.shadow_insights = []
        self.preferences = []

    def query(self, model):
        name = getattr(model, "__name__", "")
        if name == "User":
            return DummyQuery(self.users)
        if name == "Task":
            return DummyQuery(self.tasks)
        if name == "ShadowInsight":
            return DummyQuery(self.shadow_insights)
        if name == "UserPreference":
            return DummyQuery(self.preferences)
        return DummyQuery([])

    def commit(self):
        return None

    def refresh(self, obj):
        return None

    def add(self, obj):
        return None

    def delete(self, obj):
        return None


async def _db_override():
    yield DummyDB()


async def _user_override():
    return DummyUser()


def _mk_client():
    module = PlanningModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = _db_override
    app.dependency_overrides[get_current_user] = _user_override
    return TestClient(app)


# Auth V2 Routes
def test_auth_v2_verify_token_smoke():
    """Test auth v2 verify-token endpoint"""
    client = _mk_client()
    resp = client.get("/auth/verify-token")
    # Should fail without token, but endpoint should exist
    assert resp.status_code in {200, 401, 403, 422}


def test_auth_v2_me_smoke():
    """Test auth v2 me endpoint"""
    client = _mk_client()
    resp = client.get("/auth/me")
    # 200 if user override works, 401 if unauthorized, 403 if forbidden
    assert resp.status_code in {200, 401, 403}


# Users Routes
def test_users_profile_smoke():
    """Test users profile endpoint"""
    client = _mk_client()
    resp = client.get("/users/profile")
    assert resp.status_code == 200


def test_users_preferences_get_smoke():
    """Test users preferences get endpoint"""
    client = _mk_client()
    resp = client.get("/users/preferences")
    assert resp.status_code == 200


def test_users_preferences_post_smoke():
    """Test users preferences post endpoint"""
    client = _mk_client()
    resp = client.post("/users/preferences", json={"theme": "dark"})
    assert resp.status_code == 200


# Assistant Routes - Skip for now due to vendor module dependency
# def test_assistant_voice_providers_smoke():
#     """Test assistant voice providers endpoint"""
#     client = _mk_client()
#     resp = client.get("/assistant/voice/providers")
#     assert resp.status_code == 200


# def test_assistant_voice_init_smoke():
#     """Test assistant voice init endpoint"""
#     client = _mk_client()
#     resp = client.post("/assistant/voice/init", json={"provider": "mock"})
#     assert resp.status_code in {200, 400, 422}


# Google OAuth Routes
def test_google_oauth_url_smoke():
    """Test Google OAuth URL generation endpoint"""
    client = _mk_client()
    resp = client.post("/auth/google/url", json={})
    assert resp.status_code in {200, 400, 422}


# Pricing Routes
def test_pricing_models_smoke():
    """Test pricing models endpoint"""
    client = _mk_client()
    resp = client.get("/pricing/models")
    assert resp.status_code == 200


# Integration Calendar Routes
def test_integration_calendar_status_smoke():
    """Test integration calendar status endpoint"""
    client = _mk_client()
    resp = client.get("/integration/calendar/status")
    assert resp.status_code == 200


# Shadow Routes
def test_shadow_insights_smoke():
    """Test shadow insights endpoint"""
    client = _mk_client()
    resp = client.get("/shadow/insights")
    assert resp.status_code == 200


def test_shadow_unlock_status_smoke():
    """Test shadow unlock status endpoint"""
    client = _mk_client()
    resp = client.get("/shadow/unlock-status")
    assert resp.status_code == 200


# AI Routes
def test_ai_chat_smoke():
    """Test AI chat endpoint"""
    client = _mk_client()
    resp = client.post("/ai/chat", json={"messages": [{"role": "user", "content": "test"}]})
    # May fail without API key but endpoint should exist
    assert resp.status_code in {200, 400, 422, 500}


def test_ai_parse_task_smoke():
    """Test AI parse task endpoint"""
    client = _mk_client()
    resp = client.post("/ai/parse-task", json={"input": "test task"})
    # May fail without API key but endpoint should exist
    assert resp.status_code in {200, 400, 422, 500}


def test_ai_notes_get_smoke():
    """Test AI notes get endpoint"""
    client = _mk_client()
    resp = client.get("/ai/notes")
    assert resp.status_code == 200


def test_ai_notes_post_smoke():
    """Test AI notes post endpoint"""
    client = _mk_client()
    resp = client.post("/ai/notes", json={"content": "test note"})
    assert resp.status_code in {200, 201, 422}
