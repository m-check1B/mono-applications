"""
Unit tests for analytics router
Tests workspace analytics and metrics endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestAnalyticsRouterAPI:
    """Test analytics router via HTTP client"""

    def test_overview_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/analytics/overview")
        assert response.status_code == 401

    def test_overview_authenticated(self, client: TestClient, auth_headers: dict):
        """Should get analytics overview for authenticated user"""
        response = client.get("/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "workspace" in data
        assert "taskMetrics" in data
        assert "focusMetrics" in data
        assert "bottlenecks" in data

    def test_overview_with_workspace_id(self, client: TestClient, auth_headers: dict):
        """Should accept workspace_id parameter"""
        response = client.get(
            "/analytics/overview?workspaceId=test-workspace", headers=auth_headers
        )
        assert response.status_code == 200

    def test_overview_workspace_structure(self, client: TestClient, auth_headers: dict):
        """Should return workspace information"""
        response = client.get("/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        workspace = data["workspace"]
        assert "id" in workspace
        assert "name" in workspace
        assert "description" in workspace
        assert "color" in workspace
        assert "ownerId" in workspace
        assert "memberCount" in workspace

    def test_overview_task_metrics(self, client: TestClient, auth_headers: dict):
        """Should return task metrics"""
        response = client.get("/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        task_metrics = data["taskMetrics"]
        assert "total" in task_metrics
        assert "completed" in task_metrics
        assert "pending" in task_metrics
        assert "inProgress" in task_metrics
        assert "overdue" in task_metrics
        assert "avgCompletionDays" in task_metrics
        assert "velocity" in task_metrics

    def test_overview_focus_metrics(self, client: TestClient, auth_headers: dict):
        """Should return focus/time metrics"""
        response = client.get("/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        focus_metrics = data["focusMetrics"]
        assert "hoursTrackedLast7Days" in focus_metrics
        assert "avgSessionMinutes" in focus_metrics
        assert "dailyBreakdown" in focus_metrics

    def test_overview_bottlenecks(self, client: TestClient, auth_headers: dict):
        """Should return bottleneck detection"""
        response = client.get("/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        bottlenecks = data["bottlenecks"]
        assert isinstance(bottlenecks, list)

    def test_bottlenecks_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/analytics/bottlenecks")
        assert response.status_code == 401

    def test_bottlenecks_authenticated(self, client: TestClient, auth_headers: dict):
        """Should get bottlenecks for authenticated user"""
        response = client.get("/analytics/bottlenecks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "workspaceId" in data
        assert "bottlenecks" in data

    def test_bottlenecks_with_workspace_id(
        self, client: TestClient, auth_headers: dict
    ):
        """Should accept workspace_id parameter"""
        response = client.get(
            "/analytics/bottlenecks?workspaceId=test-workspace", headers=auth_headers
        )
        assert response.status_code == 200

    def test_bottlenecks_structure(self, client: TestClient, auth_headers: dict):
        """Should return bottlenecks with proper structure"""
        response = client.get("/analytics/bottlenecks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        bottlenecks = data["bottlenecks"]
        for bottleneck in bottlenecks:
            assert "taskId" in bottleneck or "title" in bottleneck
            assert "type" in bottleneck
            assert "detail" in bottleneck
            assert "severity" in bottleneck
            assert bottleneck["severity"] in ["high", "medium", "low"]

    def test_velocity_data(self, client: TestClient, auth_headers: dict):
        """Should return velocity data with last 7 days"""
        response = client.get("/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        velocity = data["taskMetrics"]["velocity"]
        assert isinstance(velocity, list)
        assert len(velocity) == 7
        for day_data in velocity:
            assert "date" in day_data
            assert "completed" in day_data

    def test_daily_breakdown(self, client: TestClient, auth_headers: dict):
        """Should return daily breakdown with last 7 days"""
        response = client.get("/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        breakdown = data["focusMetrics"]["dailyBreakdown"]
        assert isinstance(breakdown, list)
        assert len(breakdown) == 7
        for day_data in breakdown:
            assert "date" in day_data
            assert "hours" in day_data

    def test_overdue_tasks(self, client: TestClient, auth_headers: dict):
        """Should return overdue tasks list"""
        response = client.get("/analytics/overview", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        task_metrics = data["taskMetrics"]
        if task_metrics["overdue"] > 0:
            assert "overdueTasks" in task_metrics
            assert isinstance(task_metrics["overdueTasks"], list)
            for task in task_metrics["overdueTasks"]:
                assert "id" in task
                assert "title" in task
                assert "dueDate" in task
