"""
Unit tests for Comments Router
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.comment import Comment

@pytest.mark.unit
class TestCommentsRouter:
    """Test Comments Router API endpoints"""

    async def test_create_comment_success(self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session):
        """Test creating a comment"""
        # Create a task first to satisfy FK
        from app.models.task import Task
        task = Task(id="task-123", title="Test Task", userId=test_user.id)
        db.add(task)
        db.commit()

        payload = {
            "content": "This is a test comment",
            "taskId": "task-123",
            "mentions": ["user1"]
        }
        
        response = await async_client.post("/comments/", json=payload, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == payload["content"]
        assert data["taskId"] == payload["taskId"]
        assert data["userId"] == test_user.id

    async def test_create_comment_invalid_no_target(self, async_client: AsyncClient, auth_headers: dict):
        """Test creating a comment without target"""
        payload = {
            "content": "This is a test comment"
        }
        
        response = await async_client.post("/comments/", json=payload, headers=auth_headers)
        assert response.status_code == 400

    async def test_get_task_comments(self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session):
        """Test getting comments for a task"""
        # Create a task first
        from app.models.task import Task
        task = Task(id="task-abc", title="Test Task", userId=test_user.id)
        db.add(task)
        
        # Create a comment
        comment = Comment(
            id="comm-1",
            content="Task comment",
            taskId="task-abc",
            userId=test_user.id
        )
        db.add(comment)
        db.commit()
        
        response = await async_client.get("/comments/task/task-abc", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Task comment"

    async def test_update_comment_success(self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session):
        """Test updating a comment"""
        # Create a task first
        from app.models.task import Task
        task = Task(id="task-1", title="Test Task", userId=test_user.id)
        db.add(task)
        
        # Create a comment
        comment = Comment(
            id="comm-update",
            content="Old content",
            taskId="task-1",
            userId=test_user.id
        )
        db.add(comment)
        db.commit()
        
        payload = {"content": "New content"}
        response = await async_client.put(f"/comments/{comment.id}", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["content"] == "New content"

    async def test_update_comment_wrong_user(self, async_client: AsyncClient, auth_headers: dict, db: Session):
        """Test updating someone else's comment"""
        # Create another user first to satisfy Task FK
        other_user = User(
            id="other-user-id",
            email="other@example.com",
            username="otheruser",
            organizationId="other-org"
        )
        db.add(other_user)
        db.commit()

        # Create a task first
        from app.models.task import Task
        task = Task(id="task-1", title="Test Task", userId=other_user.id)
        db.add(task)
        
        # Create a comment by another user
        comment = Comment(
            id="comm-other",
            content="Other user comment",
            taskId="task-1",
            userId=other_user.id
        )
        db.add(comment)
        db.commit()
        
        payload = {"content": "New content"}
        response = await async_client.put(f"/comments/{comment.id}", json=payload, headers=auth_headers)
        
        assert response.status_code == 403

    async def test_delete_comment_success(self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session):
        """Test deleting a comment"""
        # Create a task first
        from app.models.task import Task
        task = Task(id="task-1", title="Test Task", userId=test_user.id)
        db.add(task)
        
        # Create a comment
        comment = Comment(
            id="comm-delete",
            content="To be deleted",
            taskId="task-1",
            userId=test_user.id
        )
        db.add(comment)
        db.commit()
        
        response = await async_client.delete(f"/comments/{comment.id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify it's gone
        assert db.query(Comment).filter(Comment.id == comment.id).first() is None