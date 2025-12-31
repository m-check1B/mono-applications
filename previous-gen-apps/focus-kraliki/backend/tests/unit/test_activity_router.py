"""
Unit tests for activity router
Tests team activity feed endpoints
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.models.user import User
from app.models.activity import Activity
from app.models.workspace import Workspace
from app.core.security import generate_id


class TestActivityRouterAPI:
    """Test activity router via HTTP client"""

    def test_get_activity_feed_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/activity/feed")
        assert response.status_code == 401

    def test_get_activity_feed_authenticated(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should get activity feed for authenticated user"""
        workspace_id = generate_id()
        workspace = Workspace(id=workspace_id, name="Test Workspace", ownerId=test_user.id)
        db.add(workspace)
        db.flush()
        test_user.activeWorkspaceId = workspace_id
        db.commit()

        activity = Activity(
            id=generate_id(),
            activityType="task_created",
            userId=test_user.id,
            workspaceId=workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Test Task",
            createdAt=datetime.utcnow(),
        )
        db.add(activity)
        db.commit()

        response = client.get("/activity/feed", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert "hasMore" in data
        assert "nextCursor" in data
        assert len(data["activities"]) >= 1

    def test_get_activity_feed_with_workspace_filter(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should filter activity feed by workspace"""
        workspace_id = generate_id()
        workspace = Workspace(id=workspace_id, name="Test Workspace", ownerId=test_user.id)
        db.add(workspace)
        
        other_workspace_id = generate_id()
        other_workspace = Workspace(id=other_workspace_id, name="Other Workspace", ownerId=test_user.id)
        db.add(other_workspace)
        
        db.flush()
        test_user.activeWorkspaceId = workspace_id
        db.commit()

        activity1 = Activity(
            id=generate_id(),
            activityType="task_created",
            userId=test_user.id,
            workspaceId=workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Task 1",
            createdAt=datetime.utcnow(),
        )
        activity2 = Activity(
            id=generate_id(),
            activityType="comment_added",
            userId=test_user.id,
            workspaceId=other_workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Task 2",
            createdAt=datetime.utcnow(),
        )
        db.add(activity1)
        db.add(activity2)
        db.commit()

        response = client.get(
            f"/activity/feed?workspace_id={workspace_id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["activities"]) == 1
        assert data["activities"][0]["targetTitle"] == "Task 1"

    def test_get_activity_feed_with_limit(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should respect limit parameter"""
        workspace_id = generate_id()
        workspace = Workspace(id=workspace_id, name="Test Workspace", ownerId=test_user.id)
        db.add(workspace)
        db.flush()
        test_user.activeWorkspaceId = workspace_id
        db.commit()

        for i in range(10):
            activity = Activity(
                id=generate_id(),
                activityType="task_created",
                userId=test_user.id,
                workspaceId=workspace_id,
                targetType="task",
                targetId=generate_id(),
                targetTitle=f"Task {i}",
                createdAt=datetime.utcnow() - timedelta(minutes=i),
            )
            db.add(activity)
        db.commit()

        response = client.get("/activity/feed?limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["activities"]) <= 5

    def test_get_activity_feed_with_cursor(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should support cursor-based pagination"""
        workspace_id = generate_id()
        workspace = Workspace(id=workspace_id, name="Test Workspace", ownerId=test_user.id)
        db.add(workspace)
        db.flush()
        test_user.activeWorkspaceId = workspace_id
        db.commit()

        now = datetime.utcnow()
        activity1 = Activity(
            id=generate_id(),
            activityType="task_created",
            userId=test_user.id,
            workspaceId=workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Task 1",
            createdAt=now,
        )
        activity2 = Activity(
            id=generate_id(),
            activityType="task_created",
            userId=test_user.id,
            workspaceId=workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Task 2",
            createdAt=now - timedelta(minutes=5),
        )
        db.add(activity1)
        db.add(activity2)
        db.commit()

        response = client.get("/activity/feed?limit=1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["hasMore"] is True
        next_cursor = data["nextCursor"]
        assert next_cursor is not None

        response = client.get(
            f"/activity/feed?before={next_cursor}&limit=1", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["activities"]) >= 1

    def test_get_user_activity_unauthenticated(
        self, client: TestClient, test_user: User
    ):
        """Should return 401 when not authenticated"""
        response = client.get(f"/activity/user/{test_user.id}")
        assert response.status_code == 401

    def test_get_user_activity_authenticated(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should get activity for specific user"""
        workspace_id = generate_id()
        workspace = Workspace(id=workspace_id, name="Test Workspace", ownerId=test_user.id)
        db.add(workspace)
        db.flush()
        test_user.activeWorkspaceId = workspace_id
        db.commit()

        activity = Activity(
            id=generate_id(),
            activityType="task_created",
            userId=test_user.id,
            workspaceId=workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Test Task",
            createdAt=datetime.utcnow(),
        )
        db.add(activity)
        db.commit()

        response = client.get(f"/activity/user/{test_user.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data
        assert len(data["activities"]) >= 1

    def test_get_user_activity_with_limit(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should respect limit parameter for user activity"""
        workspace_id = generate_id()
        workspace = Workspace(id=workspace_id, name="Test Workspace", ownerId=test_user.id)
        db.add(workspace)
        db.flush()
        test_user.activeWorkspaceId = workspace_id
        db.commit()

        for i in range(10):
            activity = Activity(
                id=generate_id(),
                activityType="task_created",
                userId=test_user.id,
                workspaceId=workspace_id,
                targetType="task",
                targetId=generate_id(),
                targetTitle=f"Task {i}",
                createdAt=datetime.utcnow() - timedelta(minutes=i),
            )
            db.add(activity)
        db.commit()

        response = client.get(
            f"/activity/user/{test_user.id}?limit=5", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["activities"]) <= 5

    def test_get_today_activity_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/activity/today")
        assert response.status_code == 401

    def test_get_today_activity_authenticated(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should get today's activity"""
        workspace_id = generate_id()
        workspace = Workspace(id=workspace_id, name="Test Workspace", ownerId=test_user.id)
        db.add(workspace)
        db.flush()
        test_user.activeWorkspaceId = workspace_id
        db.commit()

        activity = Activity(
            id=generate_id(),
            activityType="task_created",
            userId=test_user.id,
            workspaceId=workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Test Task",
            createdAt=datetime.utcnow(),
        )
        db.add(activity)
        db.commit()

        response = client.get("/activity/today", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "activities" in data

    def test_get_today_activity_excludes_yesterday(
        self, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should only include today's activity"""
        workspace_id = generate_id()
        workspace = Workspace(id=workspace_id, name="Test Workspace", ownerId=test_user.id)
        db.add(workspace)
        db.flush()
        test_user.activeWorkspaceId = workspace_id
        db.commit()

        today_activity = Activity(
            id=generate_id(),
            activityType="task_created",
            userId=test_user.id,
            workspaceId=workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Today's Task",
            createdAt=datetime.utcnow(),
        )
        yesterday_activity = Activity(
            id=generate_id(),
            activityType="task_created",
            userId=test_user.id,
            workspaceId=workspace_id,
            targetType="task",
            targetId=generate_id(),
            targetTitle="Yesterday's Task",
            createdAt=datetime.utcnow() - timedelta(days=1, hours=1),
        )
        db.add(today_activity)
        db.add(yesterday_activity)
        db.commit()

        response = client.get("/activity/today", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["activities"]) == 1
        assert data["activities"][0]["targetTitle"] == "Today's Task"
