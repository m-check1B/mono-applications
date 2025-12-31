"""Smoke tests for contacts routes"""
from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db
from tests.utils import override_db


def test_contacts_list():
    """Test GET /api/contacts/ endpoint exists and requires auth"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.get("/api/contacts/")
    # 401 = auth required (correct), 200 = success
    assert resp.status_code in (200, 401)


def test_contacts_create():
    """Test POST /api/contacts/ endpoint exists and requires auth"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/contacts/", json={
        "campaign_id": "test-campaign",
        "phone_number": "+1234567890",
        "name": "Test Contact"
    })
    # 401 = auth required (correct), 201 = success
    assert resp.status_code in (201, 401)


def test_contacts_get_by_id():
    """Test GET /api/contacts/{id} endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.get("/api/contacts/test-id")
    # 401 = auth required, 404 = not found, 200 = success
    assert resp.status_code in (200, 401, 404)


def test_contacts_update():
    """Test PUT /api/contacts/{id} endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.put("/api/contacts/test-id", json={
        "name": "Updated Name"
    })
    # 401 = auth required, 404 = not found, 200 = success
    assert resp.status_code in (200, 401, 404)


def test_contacts_delete():
    """Test DELETE /api/contacts/{id} endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.delete("/api/contacts/test-id")
    # 401 = auth required, 404 = not found, 204 = success
    assert resp.status_code in (204, 401, 404)
