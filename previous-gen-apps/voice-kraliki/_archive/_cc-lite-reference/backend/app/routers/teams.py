"""Teams router - FastAPI endpoints for team management"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import uuid4
from typing import Optional

from app.core.database import get_db
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamMemberAdd,
    TeamMemberResponse,
    TeamListResponse
)
from app.dependencies import get_current_user, require_supervisor

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("/", response_model=TeamListResponse)
async def list_teams(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all teams in organization

    Args:
        skip: Offset for pagination
        limit: Number of teams to return
        db: Database session
        current_user: Authenticated user

    Returns:
        List of teams with pagination info
    """
    # Query teams for user's organization
    query = select(Team).where(Team.organization_id == current_user.organization_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Team.created_at.desc())
    result = await db.execute(query)
    teams = result.scalars().all()

    return {
        "teams": teams,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get team by ID

    Args:
        team_id: Team ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Team details
    """
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id
        )
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return team


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Create a new team (supervisor/admin only)

    Args:
        team_data: Team creation data
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Created team
    """
    # Create team
    team = Team(
        id=str(uuid4()),
        name=team_data.name,
        description=team_data.description,
        organization_id=current_user.organization_id,
        supervisor_id=team_data.supervisor_id or current_user.id,
        max_members=team_data.max_members,
        skills=team_data.skills or [],
        extra_metadata=team_data.extra_metadata
    )

    db.add(team)
    await db.commit()
    await db.refresh(team)

    return team


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Update team (supervisor/admin only)

    Args:
        team_id: Team ID
        team_data: Team update data
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Updated team
    """
    # Find team
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id
        )
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Update fields
    for field, value in team_data.model_dump(exclude_unset=True).items():
        setattr(team, field, value)

    await db.commit()
    await db.refresh(team)

    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Delete team (supervisor/admin only)

    Args:
        team_id: Team ID
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)
    """
    # Find team
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id
        )
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    await db.delete(team)
    await db.commit()


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: str,
    member_data: TeamMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Add member to team (supervisor/admin only)

    Args:
        team_id: Team ID
        member_data: Member data
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)

    Returns:
        Created team member
    """
    # Verify team exists
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id
        )
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Verify user exists
    user_result = await db.execute(
        select(User).where(
            User.id == member_data.user_id,
            User.organization_id == current_user.organization_id
        )
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already a member
    existing = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == member_data.user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a team member"
        )

    # Add member
    team_member = TeamMember(
        id=str(uuid4()),
        team_id=team_id,
        user_id=member_data.user_id,
        role=member_data.role
    )

    db.add(team_member)
    await db.commit()
    await db.refresh(team_member)

    return team_member


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    """
    Remove member from team (supervisor/admin only)

    Args:
        team_id: Team ID
        user_id: User ID
        db: Database session
        current_user: Authenticated user (must be supervisor or admin)
    """
    # Verify team exists
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id
        )
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Find team member
    member_result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
    )
    team_member = member_result.scalar_one_or_none()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    await db.delete(team_member)
    await db.commit()


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
async def list_team_members(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all members of a team

    Args:
        team_id: Team ID
        db: Database session
        current_user: Authenticated user

    Returns:
        List of team members
    """
    # Verify team exists and user has access
    result = await db.execute(
        select(Team).where(
            Team.id == team_id,
            Team.organization_id == current_user.organization_id
        )
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Get team members
    members_result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id)
    )
    members = members_result.scalars().all()

    return members
