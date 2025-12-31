"""
Activity Router - Team activity feed.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.activity import Activity, ACTIVITY_TYPES
from app.schemas.activity import ActivityResponse, ActivityFeedResponse

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/feed", response_model=ActivityFeedResponse)
async def get_activity_feed(
    workspace_id: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    before: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get team activity feed.

    Shows recent activity from workspace members.
    """
    ws_id = workspace_id or current_user.activeWorkspaceId

    query = db.query(Activity)

    if ws_id:
        query = query.filter(Activity.workspaceId == ws_id)

    # Cursor-based pagination
    if before:
        try:
            before_dt = datetime.fromisoformat(before)
            query = query.filter(Activity.createdAt < before_dt)
        except ValueError:
            pass

    activities = query.order_by(Activity.createdAt.desc()).limit(limit + 1).all()

    has_more = len(activities) > limit
    if has_more:
        activities = activities[:limit]

    next_cursor = None
    if has_more and activities:
        next_cursor = activities[-1].createdAt.isoformat()

    return ActivityFeedResponse(
        activities=[
            ActivityResponse(
                id=a.id,
                activityType=a.activityType,
                activityLabel=ACTIVITY_TYPES.get(a.activityType, a.activityType),
                userId=a.userId,
                userName=a.user.username if a.user else None,
                workspaceId=a.workspaceId,
                targetType=a.targetType,
                targetId=a.targetId,
                targetTitle=a.targetTitle,
                extraData=a.extra_data,
                createdAt=a.createdAt
            )
            for a in activities
        ],
        hasMore=has_more,
        nextCursor=next_cursor
    )


@router.get("/user/{user_id}", response_model=ActivityFeedResponse)
async def get_user_activity(
    user_id: str,
    limit: int = Query(default=20, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity for a specific user."""
    activities = db.query(Activity).filter(
        Activity.userId == user_id,
        Activity.workspaceId == current_user.activeWorkspaceId
    ).order_by(Activity.createdAt.desc()).limit(limit).all()

    return ActivityFeedResponse(
        activities=[
            ActivityResponse(
                id=a.id,
                activityType=a.activityType,
                activityLabel=ACTIVITY_TYPES.get(a.activityType, a.activityType),
                userId=a.userId,
                userName=a.user.username if a.user else None,
                workspaceId=a.workspaceId,
                targetType=a.targetType,
                targetId=a.targetId,
                targetTitle=a.targetTitle,
                extraData=a.extra_data,
                createdAt=a.createdAt
            )
            for a in activities
        ],
        hasMore=False,
        nextCursor=None
    )


@router.get("/today", response_model=ActivityFeedResponse)
async def get_today_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's activity for the workspace."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    activities = db.query(Activity).filter(
        Activity.workspaceId == current_user.activeWorkspaceId,
        Activity.createdAt >= today_start
    ).order_by(Activity.createdAt.desc()).all()

    return ActivityFeedResponse(
        activities=[
            ActivityResponse(
                id=a.id,
                activityType=a.activityType,
                activityLabel=ACTIVITY_TYPES.get(a.activityType, a.activityType),
                userId=a.userId,
                userName=a.user.username if a.user else None,
                workspaceId=a.workspaceId,
                targetType=a.targetType,
                targetId=a.targetId,
                targetTitle=a.targetTitle,
                extraData=a.extra_data,
                createdAt=a.createdAt
            )
            for a in activities
        ],
        hasMore=False,
        nextCursor=None
    )
