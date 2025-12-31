"""
Comments Router - Team collaboration on tasks/projects.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.comment import Comment
from app.models.activity import Activity
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter(prefix="/comments", tags=["comments"])


def _log_activity(
    db: Session,
    user: User,
    activity_type: str,
    target_type: str,
    target_id: str,
    target_title: str = None,
    workspace_id: str = None,
    extra_data: dict = None
):
    """Log activity for team feed."""
    activity = Activity(
        id=generate_id(),
        activityType=activity_type,
        userId=user.id,
        workspaceId=workspace_id or user.activeWorkspaceId,
        targetType=target_type,
        targetId=target_id,
        targetTitle=target_title,
        extra_data=extra_data
    )
    db.add(activity)


@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a task, project, or knowledge item."""
    # Validate that at least one target is specified
    if not any([comment_data.taskId, comment_data.projectId, comment_data.knowledgeItemId]):
        raise HTTPException(status_code=400, detail="Must specify taskId, projectId, or knowledgeItemId")

    comment = Comment(
        id=generate_id(),
        content=comment_data.content,
        taskId=comment_data.taskId,
        projectId=comment_data.projectId,
        knowledgeItemId=comment_data.knowledgeItemId,
        userId=current_user.id,
        workspaceId=current_user.activeWorkspaceId,
        mentions=json.dumps(comment_data.mentions) if comment_data.mentions else None
    )
    db.add(comment)

    # Determine target for activity
    target_type = "task" if comment_data.taskId else ("project" if comment_data.projectId else "knowledge")
    target_id = comment_data.taskId or comment_data.projectId or comment_data.knowledgeItemId

    _log_activity(
        db, current_user, "comment_added", target_type, target_id,
        extra_data={"preview": comment_data.content[:100]}
    )

    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        taskId=comment.taskId,
        projectId=comment.projectId,
        knowledgeItemId=comment.knowledgeItemId,
        userId=comment.userId,
        userName=current_user.username,
        mentions=json.loads(comment.mentions) if comment.mentions else None,
        createdAt=comment.createdAt,
        updatedAt=comment.updatedAt
    )


@router.get("/task/{task_id}", response_model=List[CommentResponse])
async def get_task_comments(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a task."""
    comments = db.query(Comment).filter(
        Comment.taskId == task_id
    ).order_by(Comment.createdAt.desc()).all()

    return [
        CommentResponse(
            id=c.id,
            content=c.content,
            taskId=c.taskId,
            projectId=c.projectId,
            knowledgeItemId=c.knowledgeItemId,
            userId=c.userId,
            userName=c.user.username if c.user else None,
            mentions=json.loads(c.mentions) if c.mentions else None,
            createdAt=c.createdAt,
            updatedAt=c.updatedAt
        )
        for c in comments
    ]


@router.get("/project/{project_id}", response_model=List[CommentResponse])
async def get_project_comments(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a project."""
    comments = db.query(Comment).filter(
        Comment.projectId == project_id
    ).order_by(Comment.createdAt.desc()).all()

    return [
        CommentResponse(
            id=c.id,
            content=c.content,
            taskId=c.taskId,
            projectId=c.projectId,
            knowledgeItemId=c.knowledgeItemId,
            userId=c.userId,
            userName=c.user.username if c.user else None,
            mentions=json.loads(c.mentions) if c.mentions else None,
            createdAt=c.createdAt,
            updatedAt=c.updatedAt
        )
        for c in comments
    ]


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a comment (author only)."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Can only edit your own comments")

    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        taskId=comment.taskId,
        projectId=comment.projectId,
        knowledgeItemId=comment.knowledgeItemId,
        userId=comment.userId,
        userName=current_user.username,
        mentions=json.loads(comment.mentions) if comment.mentions else None,
        createdAt=comment.createdAt,
        updatedAt=comment.updatedAt
    )


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (author only)."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own comments")

    db.delete(comment)
    db.commit()
