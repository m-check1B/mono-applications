"""
Speak by Kraliki - Action Tests
"""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.action import Action
from app.models.employee import Employee


@pytest.mark.asyncio
async def test_list_actions(client: AsyncClient, test_action, auth_headers):
    """Test listing actions."""
    response = await client.get("/api/speak/actions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["topic"] == "Review workload policies"


@pytest.mark.asyncio
async def test_list_actions_with_filter(client: AsyncClient, test_action, auth_headers):
    """Test listing actions with status filter."""
    response = await client.get(
        "/api/speak/actions?status_filter=new", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["status"] == "new"


@pytest.mark.asyncio
async def test_create_action(client: AsyncClient, auth_headers, test_department):
    """Test creating a new action."""
    response = await client.post(
        "/api/speak/actions",
        headers=auth_headers,
        json={
            "topic": "New Office Hours",
            "description": "Implement flexible office hours policy",
            "department_id": str(test_department.id),
            "priority": "high",
            "visible_to_employees": True,
            "public_message": "We're implementing flexible office hours!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "New Office Hours"
    assert data["status"] == "new"
    assert data["priority"] == "high"
    assert data["visible_to_employees"] == True


@pytest.mark.asyncio
async def test_create_action_from_alert(
    client: AsyncClient, auth_headers, test_alert, test_department
):
    """Test creating an action from an alert."""
    response = await client.post(
        "/api/speak/actions",
        headers=auth_headers,
        json={
            "topic": "Alert-based Action",
            "description": "Action created from alert",
            "created_from_alert_id": str(test_alert.id),
            "department_id": str(test_department.id),
            "priority": "high",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Alert-based Action"
    assert data["created_from_alert_id"] == str(test_alert.id)


@pytest.mark.asyncio
async def test_get_action(client: AsyncClient, test_action, auth_headers):
    """Test getting a specific action."""
    response = await client.get(
        f"/api/speak/actions/{test_action.id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_action.id)
    assert data["topic"] == "Review workload policies"


@pytest.mark.asyncio
async def test_get_nonexistent_action(client: AsyncClient, auth_headers):
    """Test getting a non-existent action."""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/speak/actions/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_action_status(
    client: AsyncClient, test_action, auth_headers, test_session: AsyncSession
):
    """Test updating action status."""
    response = await client.patch(
        f"/api/speak/actions/{test_action.id}",
        headers=auth_headers,
        json={"status": "in_progress"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"

    result = await test_session.execute(
        select(Action).where(Action.id == test_action.id)
    )
    action = result.scalar_one()
    assert action.status == "in_progress"


@pytest.mark.asyncio
async def test_update_action_to_resolved(
    client: AsyncClient, test_action, auth_headers, test_session: AsyncSession
):
    """Test updating action to resolved status sets resolved_at timestamp."""
    response = await client.patch(
        f"/api/speak/actions/{test_action.id}",
        headers=auth_headers,
        json={"status": "resolved"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"
    assert data["resolved_at"] is not None

    result = await test_session.execute(
        select(Action).where(Action.id == test_action.id)
    )
    action = result.scalar_one()
    assert action.status == "resolved"
    assert action.resolved_at is not None


@pytest.mark.asyncio
async def test_update_action_multiple_fields(
    client: AsyncClient,
    test_action,
    auth_headers,
    test_user,
    test_session: AsyncSession,
):
    """Test updating multiple action fields."""
    response = await client.patch(
        f"/api/speak/actions/{test_action.id}",
        headers=auth_headers,
        json={
            "topic": "Updated Topic",
            "description": "Updated description",
            "status": "heard",
            "priority": "low",
            "assigned_to": str(test_user.id),
            "notes": "Working on this",
            "visible_to_employees": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Updated Topic"
    assert data["description"] == "Updated description"
    assert data["status"] == "heard"
    assert data["priority"] == "low"
    assert data["assigned_to"] == str(test_user.id)
    assert data["notes"] == "Working on this"
    assert data["visible_to_employees"] == False


@pytest.mark.asyncio
async def test_delete_action(
    client: AsyncClient, test_action, auth_headers, test_session: AsyncSession
):
    """Test deleting an action."""
    response = await client.delete(
        f"/api/speak/actions/{test_action.id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "deleted" in data["message"]

    result = await test_session.execute(
        select(Action).where(Action.id == test_action.id)
    )
    action = result.scalar_one_or_none()
    assert action is None


@pytest.mark.asyncio
async def test_delete_nonexistent_action(client: AsyncClient, auth_headers):
    """Test deleting a non-existent action."""
    fake_id = uuid.uuid4()
    response = await client.delete(
        f"/api/speak/actions/{fake_id}", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_public_actions(
    client: AsyncClient, test_action, test_employee, test_session: AsyncSession
):
    """Test listing public actions via magic link token."""
    token = "test-magic-link-token"

    test_employee.magic_link_token = "test-magic-link-token-hash"
    test_employee.magic_link_expires = None
    await test_session.commit()

    from app.core.auth import hash_magic_link_token

    test_employee.magic_link_token = hash_magic_link_token(token)
    await test_session.commit()

    response = await client.get(f"/api/speak/actions/public?token={token}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["topic"] == "Review workload policies"


@pytest.mark.asyncio
async def test_list_public_actions_invalid_token(client: AsyncClient):
    """Test listing public actions with invalid token."""
    response = await client.get("/api/speak/actions/public?token=invalid-token")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_public_actions_expired_token(
    client: AsyncClient, test_employee, test_session: AsyncSession
):
    """Test listing public actions with expired token."""
    from datetime import datetime, timezone, timedelta
    from app.core.auth import hash_magic_link_token

    token = "expired-token"
    expired_time = datetime.now(timezone.utc) - timedelta(hours=1)

    test_employee.magic_link_token = hash_magic_link_token(token)
    test_employee.magic_link_expires = expired_time
    await test_session.commit()

    response = await client.get(f"/api/speak/actions/public?token={token}")
    assert response.status_code == 410


@pytest.mark.asyncio
async def test_action_unauthorized(client: AsyncClient, test_action):
    """Test accessing actions without auth."""
    response = await client.get("/api/speak/actions")
    assert response.status_code == 401

    response = await client.get(f"/api/speak/actions/{test_action.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_action_list_enriched_with_assigned_user(
    client: AsyncClient,
    test_action,
    test_user,
    auth_headers,
    test_session: AsyncSession,
):
    """Test that action list includes assigned user name."""
    test_action.assigned_to = test_user.id
    await test_session.commit()

    response = await client.get("/api/speak/actions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["assigned_to_name"] == "Test Admin"
