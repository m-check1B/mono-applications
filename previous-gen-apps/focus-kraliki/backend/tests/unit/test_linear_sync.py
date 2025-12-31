"""
Tests for Linear Sync Router - Webhook and Outbound Sync
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.task import Task, TaskStatus

client = TestClient(app)

@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    return db

def test_linear_webhook_update_status(mock_db):
    """Test that Linear webhook updates task status correctly."""
    linear_id = "issue_123"
    
    # Mock task in DB
    mock_task = Task(
        id="task_123",
        title="Test Task",
        linear_id=linear_id,
        status=TaskStatus.PENDING
    )
    
    # Mock DB query
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = mock_task
    
    # Webhook payload
    payload = {
        "action": "update",
        "type": "Issue",
        "data": {
            "id": linear_id,
            "state": {
                "id": "state_started",
                "name": "In Progress",
                "type": "started"
            }
        }
    }
    
    # Override dependency
    from app.core.database import get_db
    from app.core.webhook_security import linear_webhook_verifier
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[linear_webhook_verifier.verify_linear_webhook] = lambda: payload
    
    response = client.post("/linear/webhook")
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert mock_task.status == TaskStatus.IN_PROGRESS
    
    # Test completed status
    payload["data"]["state"]["type"] = "completed"
    app.dependency_overrides[linear_webhook_verifier.verify_linear_webhook] = lambda: payload
    
    response = client.post("/linear/webhook")
    assert response.status_code == 200
    assert mock_task.status == TaskStatus.COMPLETED
    assert mock_task.completedAt is not None
    
    # Cleanup
    app.dependency_overrides = {}

def test_linear_webhook_ignored_types(mock_db):
    """Test that non-Issue types are ignored."""
    payload = {
        "action": "update",
        "type": "Comment",
        "data": {}
    }
    
    from app.core.webhook_security import linear_webhook_verifier
    app.dependency_overrides[linear_webhook_verifier.verify_linear_webhook] = lambda: payload
    
    response = client.post("/linear/webhook")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
    
    app.dependency_overrides = {}
