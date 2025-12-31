"""
Unit tests for Agent Tools Router
"""
import pytest
from datetime import datetime
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem
from app.models.task import Task, TaskStatus, Project
from app.models.workspace import Workspace, WorkspaceMember

@pytest.fixture
def setup_agent_tools_data(db, test_user):
    # Create item type
    item_type = ItemType(
        id="note", 
        userId=test_user.id, 
        name="Note", 
        icon="file-text"
    )
    db.add(item_type)
    
    # Create tasks type
    tasks_type = ItemType(
        id="tasks", 
        userId=test_user.id, 
        name="Tasks", 
        icon="check",
        isDefault=True
    )
    db.add(tasks_type)
    
    # Create workspace
    workspace = Workspace(
        id="ws1",
        name="Default Workspace",
        ownerId=test_user.id
    )
    db.add(workspace)
    
    member = WorkspaceMember(
        id="mem1",
        workspaceId=workspace.id,
        userId=test_user.id,
        role="OWNER"
    )
    db.add(member)
    
    db.commit()
    return {"item_type": item_type, "tasks_type": tasks_type, "workspace": workspace}

def test_create_knowledge_item(client, test_user, auth_headers, db, setup_agent_tools_data):
    response = client.post(
        "/agent-tools/knowledge/create",
        headers=auth_headers,
        json={
            "typeId": "note",
            "title": "Agent Note",
            "content": "Created by agent",
            "item_metadata": {"source": "agent"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Agent Note"
    assert data["typeId"] == "note"
    
    # Verify DB
    item = db.query(KnowledgeItem).filter_by(id=data["id"]).first()
    assert item is not None
    assert item.title == "Agent Note"

def test_list_knowledge_items(client, test_user, auth_headers, db, setup_agent_tools_data):
    # Create items
    k1 = KnowledgeItem(id="k1", userId=test_user.id, typeId="note", title="K1", content="C1", completed=False)
    k2 = KnowledgeItem(id="k2", userId=test_user.id, typeId="note", title="K2", content="C2", completed=False)
    db.add(k1)
    db.add(k2)
    db.commit()
    
    response = client.get("/agent-tools/knowledge", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

def test_create_task(client, test_user, auth_headers, db, setup_agent_tools_data):
    response = client.post(
        "/agent-tools/tasks",
        headers=auth_headers,
        json={
            "title": "Agent Task",
            "description": "Do it",
            "priority": 5,
            "estimatedMinutes": 60
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Agent Task"
    assert data["priority"] == 5
    
    # Verify DB (stored as KnowledgeItem)
    item = db.query(KnowledgeItem).filter_by(id=data["id"]).first()
    assert item is not None
    assert item.title == "Agent Task"
    assert item.item_metadata["priority"] == 5

def test_list_tasks(client, test_user, auth_headers, db, setup_agent_tools_data):
    # Create task via knowledge item
    k1 = KnowledgeItem(
        id="t1", 
        userId=test_user.id, 
        typeId="tasks", 
        title="T1", 
        content="D1", 
        item_metadata={"status": "PENDING", "priority": 3}, 
        completed=False
    )
    db.add(k1)
    db.commit()
    
    response = client.get("/agent-tools/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "T1"

def test_create_or_get_project(client, test_user, auth_headers, db):
    # Create new
    response = client.post(
        "/agent-tools/projects/create-or-get",
        headers=auth_headers,
        json={
            "name": "New Project",
            "description": "Desc",
            "color": "blue"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Project"
    
    # Get existing
    response = client.post(
        "/agent-tools/projects/create-or-get",
        headers=auth_headers,
        json={
            "name": "New Project"
        }
    )
    assert response.status_code == 200
    data2 = response.json()
    assert data2["id"] == data["id"]

def test_create_event_for_agent(client, test_user, auth_headers, db):
    response = client.post(
        "/agent-tools/events",
        headers=auth_headers,
        json={
            "title": "Meeting",
            "start_time": datetime(2025, 1, 1, 10, 0).isoformat(),
            "end_time": datetime(2025, 1, 1, 11, 0).isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Meeting"

def test_start_timer_for_agent(client, test_user, auth_headers, db, setup_agent_tools_data):
    # User needs active workspace or membership
    test_user.activeWorkspaceId = "ws1"
    db.commit()
    
    response = client.post(
        "/agent-tools/time/start",
        headers=auth_headers,
        json={
            "description": "Working",
            "workspace_id": "ws1",
            "start_time": datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Working"
    assert data["end_time"] is None
