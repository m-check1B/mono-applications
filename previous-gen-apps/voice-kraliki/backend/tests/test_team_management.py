"""Tests for team and agent management system."""

import pytest
from datetime import datetime, date, time
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team, TeamMember, AgentProfile, TeamRole, AgentStatus
from app.models.shift import Shift, AgentPerformance, TeamPerformance, ShiftStatus
from app.services.team_management import TeamManagementService


@pytest.fixture
def team_service():
    """Get team management service instance."""
    return TeamManagementService()


@pytest.fixture
async def sample_team(db_session: AsyncSession):
    """Create a sample team for testing."""
    team = Team(
        name="Test Team",
        description="Test team description",
        timezone="UTC",
        working_hours={"start": "09:00", "end": "17:00"},
        working_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def sample_user(db_session: AsyncSession):
    """Create a sample user for testing."""
    import uuid
    from app.models.user import User

    user = User(
        id=str(uuid.uuid4()),
        email=f"test_{datetime.now().timestamp()}@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def sample_agent_profile(db_session: AsyncSession, sample_user, sample_team):
    """Create a sample agent profile for testing."""
    import uuid

    agent = AgentProfile(
        user_id=sample_user.id,
        team_id=sample_team.id,
        employee_id=f"EMP-{uuid.uuid4().hex[:8]}",
        display_name="Test Agent",
        current_status=AgentStatus.OFFLINE,
        skills=["sales", "support"],
        languages=["en", "es"],
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


# ===== Team Tests =====


@pytest.mark.asyncio
async def test_create_team(db_session: AsyncSession, team_service: TeamManagementService):
    """Test creating a new team."""
    from app.models.team import TeamCreate

    team_data = TeamCreate(
        name="Sales Team",
        description="Main sales team",
        timezone="America/New_York",
        working_hours={"start": "08:00", "end": "18:00"},
        working_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
    )

    team = await team_service.create_team(db_session, team_data)

    assert team.id is not None
    assert team.name == "Sales Team"
    assert team.timezone == "America/New_York"
    assert team.is_active is True
    assert team.total_agents == 0


@pytest.mark.asyncio
async def test_create_team_with_parent(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team
):
    """Test creating a team with a parent team."""
    from app.models.team import TeamCreate

    team_data = TeamCreate(
        name="Sub Team",
        description="Sub team description",
        parent_team_id=sample_team.id,
        timezone="UTC",
        working_hours={"start": "09:00", "end": "17:00"},
        working_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
    )

    team = await team_service.create_team(db_session, team_data)

    assert team.id is not None
    assert team.parent_team_id == sample_team.id
    assert team.name == "Sub Team"


@pytest.mark.asyncio
async def test_get_team(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team
):
    """Test retrieving a team by ID."""
    team = await team_service.get_team(db_session, sample_team.id)

    assert team is not None
    assert team.id == sample_team.id
    assert team.name == sample_team.name


@pytest.mark.asyncio
async def test_update_team(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team
):
    """Test updating a team."""
    from app.models.team import TeamUpdate

    update_data = TeamUpdate(name="Updated Team Name", description="Updated description")

    updated = await team_service.update_team(db_session, sample_team.id, update_data)

    assert updated is not None
    assert updated.name == "Updated Team Name"
    assert updated.description == "Updated description"


@pytest.mark.asyncio
async def test_delete_team(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team
):
    """Test deleting a team."""
    deleted = await team_service.delete_team(db_session, sample_team.id)

    assert deleted is True

    # Verify team is deleted
    team = await team_service.get_team(db_session, sample_team.id)
    assert team is None


@pytest.mark.asyncio
async def test_get_team_hierarchy(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team
):
    """Test getting team hierarchy."""
    from app.models.team import TeamCreate

    # Create child teams
    child1_data = TeamCreate(
        name="Child 1",
        parent_team_id=sample_team.id,
        timezone="UTC",
        working_hours={"start": "09:00", "end": "17:00"},
        working_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
    )
    await team_service.create_team(db_session, child1_data)

    hierarchy = await team_service.get_team_hierarchy(db_session, sample_team.id)

    assert hierarchy is not None
    assert hierarchy["id"] == sample_team.id
    assert len(hierarchy["child_teams"]) == 1
    assert hierarchy["child_teams"][0]["name"] == "Child 1"


# ===== Team Member Tests =====


@pytest.mark.asyncio
async def test_add_team_member(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team, sample_user
):
    """Test adding a member to a team."""
    from app.models.team import TeamMemberCreate

    member_data = TeamMemberCreate(
        team_id=sample_team.id, user_id=sample_user.id, role=TeamRole.AGENT
    )

    member = await team_service.add_team_member(db_session, member_data)

    assert member.id is not None
    assert member.team_id == sample_team.id
    assert member.user_id == sample_user.id
    assert member.role == TeamRole.AGENT
    assert member.is_active is True


@pytest.mark.asyncio
async def test_get_team_members(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team, sample_user
):
    """Test getting all members of a team."""
    from app.models.team import TeamMemberCreate

    # Add a member
    member_data = TeamMemberCreate(
        team_id=sample_team.id, user_id=sample_user.id, role=TeamRole.AGENT
    )
    await team_service.add_team_member(db_session, member_data)

    members = await team_service.get_team_members(db_session, sample_team.id)

    assert len(members) == 1
    assert members[0].team_id == sample_team.id


@pytest.mark.asyncio
async def test_remove_team_member(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team, sample_user
):
    """Test removing a member from a team."""
    from app.models.team import TeamMemberCreate

    # Add a member
    member_data = TeamMemberCreate(
        team_id=sample_team.id, user_id=sample_user.id, role=TeamRole.AGENT
    )
    member = await team_service.add_team_member(db_session, member_data)

    # Remove the member
    deleted = await team_service.remove_team_member(db_session, member.id)

    assert deleted is True

    # Verify member is removed
    members = await team_service.get_team_members(db_session, sample_team.id)
    assert len(members) == 0


# ===== Agent Profile Tests =====


@pytest.mark.asyncio
async def test_create_agent_profile(
    db_session: AsyncSession, team_service: TeamManagementService, sample_user, sample_team: Team
):
    """Test creating an agent profile."""
    from app.models.team import AgentProfileCreate

    profile_data = AgentProfileCreate(
        user_id=sample_user.id,
        team_id=sample_team.id,
        employee_id="EMP123",
        display_name="Agent Smith",
        phone_number="+1234567890",
        skills=["sales", "customer_service"],
        languages=["en", "es"],
        max_concurrent_calls=2,
    )

    profile = await team_service.create_agent_profile(db_session, profile_data)

    assert profile.id is not None
    assert profile.user_id == sample_user.id
    assert profile.employee_id == "EMP123"
    assert profile.display_name == "Agent Smith"
    assert len(profile.skills) == 2
    assert profile.current_status == AgentStatus.OFFLINE


@pytest.mark.asyncio
async def test_get_agent_profile(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test retrieving an agent profile."""
    profile = await team_service.get_agent_profile(db_session, sample_agent_profile.id)

    assert profile is not None
    assert profile.id == sample_agent_profile.id
    assert profile.display_name == sample_agent_profile.display_name


@pytest.mark.asyncio
async def test_update_agent_status(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test updating agent status."""
    updated = await team_service.update_agent_status(
        db_session, sample_agent_profile.id, AgentStatus.AVAILABLE
    )

    assert updated is not None
    assert updated.current_status == AgentStatus.AVAILABLE
    assert updated.status_since is not None


@pytest.mark.asyncio
async def test_get_available_agents(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test getting available agents."""
    # Set agent to available
    await team_service.update_agent_status(
        db_session, sample_agent_profile.id, AgentStatus.AVAILABLE
    )

    agents = await team_service.get_available_agents(db_session)

    assert len(agents) > 0
    assert any(a.id == sample_agent_profile.id for a in agents)


# ===== Shift Tests =====


@pytest.mark.asyncio
async def test_create_shift(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test creating a shift."""
    from app.models.shift import ShiftCreate

    shift_data = ShiftCreate(
        agent_id=sample_agent_profile.id,
        team_id=sample_agent_profile.team_id,
        shift_date=date.today(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        timezone="UTC",
    )

    shift = await team_service.create_shift(db_session, shift_data)

    assert shift.id is not None
    assert shift.agent_id == sample_agent_profile.id
    assert shift.status == ShiftStatus.SCHEDULED
    assert shift.start_time == time(9, 0)


@pytest.mark.asyncio
async def test_clock_in(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test clocking in for a shift."""
    from app.models.shift import ShiftCreate

    # Create a shift
    shift_data = ShiftCreate(
        agent_id=sample_agent_profile.id,
        team_id=sample_agent_profile.team_id,
        shift_date=date.today(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        timezone="UTC",
    )
    shift = await team_service.create_shift(db_session, shift_data)

    # Clock in
    updated_shift = await team_service.clock_in(db_session, shift.id)

    assert updated_shift is not None
    assert updated_shift.status == ShiftStatus.IN_PROGRESS
    assert updated_shift.clock_in_time is not None


@pytest.mark.asyncio
async def test_clock_out(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test clocking out from a shift."""
    from app.models.shift import ShiftCreate

    # Create and clock in
    shift_data = ShiftCreate(
        agent_id=sample_agent_profile.id,
        team_id=sample_agent_profile.team_id,
        shift_date=date.today(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        timezone="UTC",
    )
    shift = await team_service.create_shift(db_session, shift_data)
    await team_service.clock_in(db_session, shift.id)

    # Clock out
    updated_shift = await team_service.clock_out(db_session, shift.id)

    assert updated_shift is not None
    assert updated_shift.status == ShiftStatus.COMPLETED
    assert updated_shift.clock_out_time is not None


@pytest.mark.asyncio
async def test_get_shifts_for_agent(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test getting shifts for an agent."""
    from app.models.shift import ShiftCreate

    # Create multiple shifts
    for i in range(3):
        shift_data = ShiftCreate(
            agent_id=sample_agent_profile.id,
            team_id=sample_agent_profile.team_id,
            shift_date=date.today(),
            start_time=time(9 + i, 0),
            end_time=time(17 + i, 0),
            timezone="UTC",
        )
        await team_service.create_shift(db_session, shift_data)

    shifts = await team_service.get_shifts_for_agent(db_session, sample_agent_profile.id)

    assert len(shifts) == 3


@pytest.mark.asyncio
async def test_get_current_shifts(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test getting current active shifts."""
    from app.models.shift import ShiftCreate

    # Create and clock in to a shift
    shift_data = ShiftCreate(
        agent_id=sample_agent_profile.id,
        team_id=sample_agent_profile.team_id,
        shift_date=date.today(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        timezone="UTC",
    )
    shift = await team_service.create_shift(db_session, shift_data)
    await team_service.clock_in(db_session, shift.id)

    current_shifts = await team_service.get_current_shifts(db_session)

    assert len(current_shifts) > 0
    assert any(s.id == shift.id for s in current_shifts)


# ===== Performance Tests =====


@pytest.mark.asyncio
async def test_get_agent_performance(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test getting agent performance metrics."""
    # Create performance record
    performance = AgentPerformance(
        agent_id=sample_agent_profile.id,
        team_id=sample_agent_profile.team_id,
        period_date=date.today(),
        period_type="daily",
        total_calls=50,
        answered_calls=45,
        missed_calls=5,
        total_talk_time=18000,
        customer_satisfaction_score=4.5,
    )
    db_session.add(performance)
    await db_session.commit()

    # Get performance
    perf = await team_service.get_agent_performance(
        db_session, sample_agent_profile.id, date.today()
    )

    assert perf is not None
    assert perf.total_calls == 50
    assert perf.customer_satisfaction_score == 4.5


@pytest.mark.asyncio
async def test_get_team_performance(
    db_session: AsyncSession, team_service: TeamManagementService, sample_team: Team
):
    """Test getting team performance metrics."""
    # Create performance record
    performance = TeamPerformance(
        team_id=sample_team.id,
        period_date=date.today(),
        period_type="daily",
        total_agents=10,
        active_agents=8,
        total_calls=200,
        calls_answered=180,
        average_csat=4.2,
    )
    db_session.add(performance)
    await db_session.commit()

    # Get performance
    perf = await team_service.get_team_performance(db_session, sample_team.id, date.today())

    assert perf is not None
    assert perf.total_calls == 200
    assert perf.average_csat == 4.2


@pytest.mark.asyncio
async def test_update_team_metrics(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_team: Team,
    sample_agent_profile: AgentProfile,
):
    """Test updating team metrics."""
    # Update metrics
    await team_service.update_team_metrics(db_session, sample_team.id)

    # Refresh and verify
    await db_session.refresh(sample_team)

    assert sample_team.total_agents >= 0


@pytest.mark.asyncio
async def test_assign_agent_to_team(
    db_session: AsyncSession,
    team_service: TeamManagementService,
    sample_agent_profile: AgentProfile,
):
    """Test assigning an agent to a different team."""
    from app.models.team import TeamCreate

    # Create a new team
    new_team_data = TeamCreate(
        name="New Team",
        description="Test new team",
        timezone="UTC",
        working_hours={"start": "09:00", "end": "17:00"},
        working_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
    )
    new_team = await team_service.create_team(db_session, new_team_data)

    # Assign agent to new team
    updated = await team_service.assign_agent_to_team(
        db_session, sample_agent_profile.id, new_team.id, TeamRole.AGENT
    )

    assert updated is not None
    assert updated.team_id == new_team.id
