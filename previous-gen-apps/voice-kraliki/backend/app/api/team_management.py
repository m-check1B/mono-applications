"""Team and agent management API endpoints."""

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_auth import require_user
from app.database import get_db
from app.middleware.rate_limit import WRITE_OPERATION_RATE_LIMIT, limiter
from app.models.shift import (
    AgentPerformanceResponse,
    ShiftCreate,
    ShiftResponse,
    ShiftStatus,
    ShiftUpdate,
    TeamPerformanceResponse,
)
from app.models.team import (
    AgentAssignment,
    AgentProfileCreate,
    AgentProfileResponse,
    AgentProfileUpdate,
    AgentStatus,
    AgentStatusUpdate,
    TeamCreate,
    TeamHierarchy,
    TeamMemberCreate,
    TeamMemberResponse,
    TeamMemberUpdate,
    TeamResponse,
    TeamRole,
    TeamUpdate,
)
from app.models.user import User
from app.services.team_management import get_team_service

router = APIRouter(prefix="/team-management", tags=["Team Management"])


# ===== Team Endpoints =====

@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def create_team(
    request: Request,
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Create a new team. Rate limited to prevent abuse."""
    service = get_team_service()
    team = await service.create_team(db, team_data)
    return team


@router.get("/teams", response_model=list[TeamResponse])
async def list_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    parent_team_id: int | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get all teams with optional filtering."""
    service = get_team_service()
    teams = await service.get_teams(
        db,
        skip=skip,
        limit=limit,
        parent_team_id=parent_team_id,
        is_active=is_active
    )
    return teams


@router.get("/teams/hierarchy", response_model=list[TeamHierarchy])
async def get_team_hierarchy(
    root_team_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get team hierarchy as nested structure."""
    service = get_team_service()
    hierarchy = await service.get_team_hierarchy(db, root_team_id)
    return hierarchy


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get a specific team by ID."""
    service = get_team_service()
    team = await service.get_team(db, team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return team


@router.put("/teams/{team_id}", response_model=TeamResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_team(
    request: Request,
    team_id: int,
    team_data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Update a team. Rate limited to prevent abuse."""
    service = get_team_service()
    team = await service.update_team(db, team_id, team_data)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return team


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def delete_team(
    request: Request,
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Delete a team. Rate limited to prevent abuse."""
    service = get_team_service()
    deleted = await service.delete_team(db, team_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )


# ===== Team Member Endpoints =====

@router.post("/team-members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def add_team_member(
    request: Request,
    member_data: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Add a member to a team. Rate limited to prevent abuse."""
    service = get_team_service()
    member = await service.add_team_member(db, member_data)
    return member


@router.get("/teams/{team_id}/members", response_model=list[TeamMemberResponse])
async def list_team_members(
    team_id: int,
    role: TeamRole | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get team members with optional filtering."""
    service = get_team_service()
    members = await service.get_team_members(db, team_id, role=role, is_active=is_active)
    return members


@router.put("/team-members/{member_id}", response_model=TeamMemberResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_team_member(
    request: Request,
    member_id: int,
    member_data: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Update a team member. Rate limited to prevent abuse."""
    service = get_team_service()
    member = await service.update_team_member(db, member_id, member_data)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    return member


@router.delete("/team-members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def remove_team_member(
    request: Request,
    member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Remove a member from a team. Rate limited to prevent abuse."""
    service = get_team_service()
    deleted = await service.remove_team_member(db, member_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )


# ===== Agent Profile Endpoints =====

@router.post("/agents", response_model=AgentProfileResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def create_agent_profile(
    request: Request,
    profile_data: AgentProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Create an agent profile. Rate limited to prevent abuse."""
    service = get_team_service()
    try:
        agent = await service.create_agent_profile(db, profile_data)
        return agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/agents", response_model=list[AgentProfileResponse])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    team_id: int | None = None,
    status: AgentStatus | None = None,
    is_available: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get agent profiles with optional filtering."""
    service = get_team_service()
    agents = await service.get_agents(
        db,
        skip=skip,
        limit=limit,
        team_id=team_id,
        status=status,
        is_available=is_available
    )
    return agents


@router.get("/agents/{agent_id}", response_model=AgentProfileResponse)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get a specific agent profile."""
    service = get_team_service()
    agent = await service.get_agent_profile(db, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


@router.get("/agents/user/{user_id}", response_model=AgentProfileResponse)
async def get_agent_by_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get agent profile by user ID."""
    service = get_team_service()
    agent = await service.get_agent_profile_by_user_id(db, user_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


@router.put("/agents/{agent_id}", response_model=AgentProfileResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_agent(
    request: Request,
    agent_id: int,
    profile_data: AgentProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Update an agent profile. Rate limited to prevent abuse."""
    service = get_team_service()
    agent = await service.update_agent_profile(db, agent_id, profile_data)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


@router.post("/agents/{agent_id}/status", response_model=AgentProfileResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_agent_status(
    request: Request,
    agent_id: int,
    status_update: AgentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Update agent status. Rate limited to prevent abuse."""
    service = get_team_service()
    profile_data = AgentProfileUpdate(current_status=status_update.status)
    agent = await service.update_agent_profile(db, agent_id, profile_data)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


@router.post("/agents/{agent_id}/assign", response_model=AgentProfileResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def assign_agent_to_team(
    request: Request,
    agent_id: int,
    assignment: AgentAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Assign an agent to a team. Rate limited to prevent abuse."""
    service = get_team_service()
    agent = await service.assign_agent_to_team(
        db,
        agent_id,
        assignment.team_id,
        assignment.role
    )

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


# ===== Shift Endpoints =====

@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def create_shift(
    request: Request,
    shift_data: ShiftCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Create a shift. Rate limited to prevent abuse."""
    service = get_team_service()
    shift = await service.create_shift(db, shift_data)
    return shift


@router.get("/shifts", response_model=list[ShiftResponse])
async def list_shifts(
    agent_id: int | None = None,
    team_id: int | None = None,
    shift_date: date | None = None,
    status: ShiftStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get shifts with optional filtering."""
    service = get_team_service()
    shifts = await service.get_shifts(
        db,
        agent_id=agent_id,
        team_id=team_id,
        shift_date=shift_date,
        status=status,
        skip=skip,
        limit=limit
    )
    return shifts


@router.get("/shifts/current")
async def get_current_shifts(
    team_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get active shifts for today."""
    service = get_team_service()
    today = datetime.now(UTC).date()
    shifts = await service.get_shifts(
        db,
        team_id=team_id,
        shift_date=today,
        status=ShiftStatus.IN_PROGRESS
    )
    return {"shifts": shifts, "total": len(shifts)}


@router.get("/shifts/{shift_id}", response_model=ShiftResponse)
async def get_shift(
    shift_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get a specific shift."""
    service = get_team_service()
    shift = await service.get_shift(db, shift_id)

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )

    return shift


@router.put("/shifts/{shift_id}", response_model=ShiftResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_shift(
    request: Request,
    shift_id: int,
    shift_data: ShiftUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Update a shift. Rate limited to prevent abuse."""
    service = get_team_service()
    shift = await service.update_shift(db, shift_id, shift_data)

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )

    return shift


@router.post("/shifts/{shift_id}/clock-in", response_model=ShiftResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def clock_in(
    request: Request,
    shift_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Clock in for a shift. Rate limited to prevent abuse."""
    service = get_team_service()
    shift = await service.clock_in(db, shift_id)

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )

    return shift


@router.post("/shifts/{shift_id}/clock-out", response_model=ShiftResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def clock_out(
    request: Request,
    shift_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Clock out from a shift. Rate limited to prevent abuse."""
    service = get_team_service()
    shift = await service.clock_out(db, shift_id)

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )

    return shift


# ===== Performance Endpoints =====

@router.get("/agents/{agent_id}/performance", response_model=AgentPerformanceResponse)
async def get_agent_performance(
    agent_id: int,
    period_date: date,
    period_type: str = "daily",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get agent performance for a specific period."""
    service = get_team_service()
    performance = await service.get_agent_performance(
        db,
        agent_id,
        period_date,
        period_type
    )

    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance data not found"
        )

    return performance


@router.get("/teams/{team_id}/performance", response_model=TeamPerformanceResponse)
async def get_team_performance(
    team_id: int,
    period_date: date,
    period_type: str = "daily",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get team performance for a specific period."""
    service = get_team_service()
    performance = await service.get_team_performance(
        db,
        team_id,
        period_date,
        period_type
    )

    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance data not found"
        )

    return performance
