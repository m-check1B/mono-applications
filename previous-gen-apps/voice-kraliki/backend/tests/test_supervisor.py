"""Tests for supervisor cockpit functionality."""

import pytest
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supervisor import (
    CallQueue, ActiveCall, SupervisorIntervention, PerformanceAlert,
    CallQueueStatus, ActiveCallStatus, InterventionType,
    AlertSeverity, AlertType,
    CallQueueCreate, ActiveCallCreate, SupervisorInterventionCreate,
    PerformanceAlertCreate
)
from app.models.team import AgentProfile, AgentStatus
from app.models.call_state import CallDirection
from app.services.supervisor import SupervisorService


@pytest.fixture
def supervisor_service():
    """Get supervisor service instance."""
    return SupervisorService()


@pytest.fixture
async def sample_agent_profile(db_session: AsyncSession):
    """Create a sample agent profile for testing."""
    import uuid
    from app.models.user import User
    from app.models.team import Team

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=f"agent_{datetime.now().timestamp()}@example.com",
        password_hash="hashed",
        full_name="Test Agent",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create team
    team = Team(
        name="Test Team",
        timezone="UTC",
        working_hours={"start": "09:00", "end": "17:00"},
        working_days=[1, 2, 3, 4, 5]
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    # Create agent
    agent = AgentProfile(
        user_id=user.id,
        team_id=team.id,
        employee_id="EMP001",
        display_name="Test Agent",
        current_status=AgentStatus.AVAILABLE,
        skills=["sales"],
        languages=["en"]
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)

    return agent


# ===== Call Queue Tests =====

@pytest.mark.asyncio
async def test_add_to_queue(db_session: AsyncSession, supervisor_service: SupervisorService):
    """Test adding a call to the queue."""
    queue_data = CallQueueCreate(
        caller_phone="+1234567890",
        caller_name="John Doe",
        direction=CallDirection.INBOUND,
        priority=0
    )

    queue_entry = await supervisor_service.add_to_queue(db_session, queue_data)

    assert queue_entry.id is not None
    assert queue_entry.caller_phone == "+1234567890"
    assert queue_entry.status == CallQueueStatus.WAITING
    assert queue_entry.queue_position == 1


@pytest.mark.asyncio
async def test_get_queue_entries(
    db_session: AsyncSession,
    supervisor_service: SupervisorService
):
    """Test getting queue entries."""
    # Create multiple queue entries
    for i in range(3):
        queue_data = CallQueueCreate(
            caller_phone=f"+123456789{i}",
            caller_name=f"Caller {i}",
            direction=CallDirection.INBOUND,
            priority=i
        )
        await supervisor_service.add_to_queue(db_session, queue_data)

    entries = await supervisor_service.get_queue_entries(db_session)

    assert len(entries) == 3


@pytest.mark.asyncio
async def test_assign_to_agent(
    db_session: AsyncSession,
    supervisor_service: SupervisorService,
    sample_agent_profile: AgentProfile
):
    """Test assigning a queued call to an agent."""
    # Create queue entry
    queue_data = CallQueueCreate(
        caller_phone="+1234567890",
        caller_name="John Doe",
        direction=CallDirection.INBOUND
    )
    queue_entry = await supervisor_service.add_to_queue(db_session, queue_data)

    # Assign to agent
    assigned = await supervisor_service.assign_to_agent(
        db_session,
        queue_entry.id,
        sample_agent_profile.id
    )

    assert assigned is not None
    assert assigned.status == CallQueueStatus.ASSIGNED
    assert assigned.assigned_agent_id == sample_agent_profile.id
    assert assigned.assigned_at is not None


@pytest.mark.asyncio
async def test_get_queue_statistics(
    db_session: AsyncSession,
    supervisor_service: SupervisorService
):
    """Test getting queue statistics."""
    # Create queue entries
    for i in range(5):
        queue_data = CallQueueCreate(
            caller_phone=f"+123456789{i}",
            caller_name=f"Caller {i}",
            direction=CallDirection.INBOUND
        )
        await supervisor_service.add_to_queue(db_session, queue_data)

    stats = await supervisor_service.get_queue_statistics(db_session)

    assert stats["waiting_count"] == 5
    assert "average_wait_seconds" in stats
    assert "abandon_rate_percentage" in stats


# ===== Active Call Tests =====

@pytest.mark.asyncio
async def test_create_active_call(
    db_session: AsyncSession,
    supervisor_service: SupervisorService,
    sample_agent_profile: AgentProfile
):
    """Test creating an active call."""
    call_data = ActiveCallCreate(
        call_sid="CALL123",
        agent_id=sample_agent_profile.id,
        direction=CallDirection.INBOUND,
        caller_phone="+1234567890",
        caller_name="John Doe"
    )

    call = await supervisor_service.create_active_call(db_session, call_data)

    assert call.id is not None
    assert call.call_sid == "CALL123"
    assert call.agent_id == sample_agent_profile.id
    assert call.status == ActiveCallStatus.RINGING


@pytest.mark.asyncio
async def test_get_active_calls(
    db_session: AsyncSession,
    supervisor_service: SupervisorService,
    sample_agent_profile: AgentProfile
):
    """Test getting active calls."""
    # Create multiple active calls
    for i in range(3):
        call_data = ActiveCallCreate(
            call_sid=f"CALL{i}",
            agent_id=sample_agent_profile.id,
            direction=CallDirection.INBOUND,
            caller_phone=f"+123456789{i}"
        )
        await supervisor_service.create_active_call(db_session, call_data)

    calls = await supervisor_service.get_active_calls(db_session)

    assert len(calls) >= 3


@pytest.mark.asyncio
async def test_get_call_by_sid(
    db_session: AsyncSession,
    supervisor_service: SupervisorService,
    sample_agent_profile: AgentProfile
):
    """Test getting call by SID."""
    call_data = ActiveCallCreate(
        call_sid="UNIQUE_CALL_SID",
        agent_id=sample_agent_profile.id,
        direction=CallDirection.INBOUND,
        caller_phone="+1234567890"
    )
    created = await supervisor_service.create_active_call(db_session, call_data)

    found = await supervisor_service.get_call_by_sid(db_session, "UNIQUE_CALL_SID")

    assert found is not None
    assert found.id == created.id


# ===== Agent Monitoring Tests =====

@pytest.mark.asyncio
async def test_get_agent_live_status(
    db_session: AsyncSession,
    supervisor_service: SupervisorService,
    sample_agent_profile: AgentProfile
):
    """Test getting agent live status."""
    statuses = await supervisor_service.get_agent_live_status(db_session)

    assert len(statuses) > 0
    assert any(s["agent_id"] == sample_agent_profile.id for s in statuses)


# ===== Supervisor Intervention Tests =====

@pytest.mark.asyncio
async def test_start_intervention(
    db_session: AsyncSession,
    supervisor_service: SupervisorService,
    sample_agent_profile: AgentProfile
):
    """Test starting a supervisor intervention."""
    import uuid
    from app.models.user import User

    # Create supervisor user
    supervisor = User(
        id=str(uuid.uuid4()),
        email=f"supervisor_{datetime.now().timestamp()}@example.com",
        password_hash="hashed",
        full_name="Supervisor",
        is_active=True
    )
    db_session.add(supervisor)
    await db_session.commit()
    await db_session.refresh(supervisor)

    # Create active call
    call_data = ActiveCallCreate(
        call_sid="CALL_TO_MONITOR",
        agent_id=sample_agent_profile.id,
        direction=CallDirection.INBOUND,
        caller_phone="+1234567890"
    )
    call = await supervisor_service.create_active_call(db_session, call_data)

    # Start intervention
    intervention_data = SupervisorInterventionCreate(
        call_id=call.id,
        intervention_type=InterventionType.MONITOR,
        reason="Quality monitoring"
    )

    intervention = await supervisor_service.start_intervention(
        db_session,
        intervention_data,
        supervisor.id
    )

    assert intervention.id is not None
    assert intervention.call_id == call.id
    assert intervention.supervisor_id == supervisor.id
    assert intervention.intervention_type == InterventionType.MONITOR


@pytest.mark.asyncio
async def test_end_intervention(
    db_session: AsyncSession,
    supervisor_service: SupervisorService,
    sample_agent_profile: AgentProfile
):
    """Test ending a supervisor intervention."""
    import uuid
    from app.models.user import User

    # Create supervisor
    supervisor = User(
        id=str(uuid.uuid4()),
        email=f"supervisor2_{datetime.now().timestamp()}@example.com",
        password_hash="hashed",
        full_name="Supervisor",
        is_active=True
    )
    db_session.add(supervisor)
    await db_session.commit()
    await db_session.refresh(supervisor)

    # Create call and intervention
    call_data = ActiveCallCreate(
        call_sid="CALL_MONITOR2",
        agent_id=sample_agent_profile.id,
        direction=CallDirection.INBOUND,
        caller_phone="+1234567890"
    )
    call = await supervisor_service.create_active_call(db_session, call_data)

    intervention_data = SupervisorInterventionCreate(
        call_id=call.id,
        intervention_type=InterventionType.MONITOR,
        reason="Testing"
    )
    intervention = await supervisor_service.start_intervention(
        db_session,
        intervention_data,
        supervisor.id
    )

    # End intervention
    ended = await supervisor_service.end_intervention(db_session, intervention.id)

    assert ended is not None
    assert ended.ended_at is not None
    assert ended.duration_seconds is not None


# ===== Performance Alert Tests =====

@pytest.mark.asyncio
async def test_create_alert(
    db_session: AsyncSession,
    supervisor_service: SupervisorService
):
    """Test creating a performance alert."""
    alert_data = PerformanceAlertCreate(
        alert_type=AlertType.LONG_WAIT_TIME,
        severity=AlertSeverity.WARNING,
        title="Long Wait Time Detected",
        message="Average wait time exceeded 5 minutes"
    )

    alert = await supervisor_service.create_alert(db_session, alert_data)

    assert alert.id is not None
    assert alert.alert_type == AlertType.LONG_WAIT_TIME
    assert alert.is_active is True


@pytest.mark.asyncio
async def test_acknowledge_alert(
    db_session: AsyncSession,
    supervisor_service: SupervisorService
):
    """Test acknowledging an alert."""
    import uuid
    from app.models.user import User

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=f"user_{datetime.now().timestamp()}@example.com",
        password_hash="hashed",
        full_name="User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create alert
    alert_data = PerformanceAlertCreate(
        alert_type=AlertType.QUEUE_OVERFLOW,
        severity=AlertSeverity.CRITICAL,
        title="Queue Overflow",
        message="Queue size exceeded threshold"
    )
    alert = await supervisor_service.create_alert(db_session, alert_data)

    # Acknowledge
    acked = await supervisor_service.acknowledge_alert(db_session, alert.id, user.id)

    assert acked is not None
    assert acked.is_acknowledged is True
    assert acked.acknowledged_at is not None
    assert acked.acknowledged_by_id == user.id


@pytest.mark.asyncio
async def test_resolve_alert(
    db_session: AsyncSession,
    supervisor_service: SupervisorService
):
    """Test resolving an alert."""
    alert_data = PerformanceAlertCreate(
        alert_type=AlertType.SLA_BREACH,
        severity=AlertSeverity.WARNING,
        title="SLA Breach",
        message="SLA threshold breached"
    )
    alert = await supervisor_service.create_alert(db_session, alert_data)

    # Resolve
    resolved = await supervisor_service.resolve_alert(
        db_session,
        alert.id,
        "Issue resolved"
    )

    assert resolved is not None
    assert resolved.is_resolved is True
    assert resolved.is_active is False
    assert resolved.resolved_at is not None
    assert resolved.resolution_notes == "Issue resolved"


# ===== Dashboard Stats Tests =====

@pytest.mark.asyncio
async def test_get_dashboard_stats(
    db_session: AsyncSession,
    supervisor_service: SupervisorService,
    sample_agent_profile: AgentProfile
):
    """Test getting dashboard statistics."""
    # Create some test data
    call_data = ActiveCallCreate(
        call_sid="DASHBOARD_TEST",
        agent_id=sample_agent_profile.id,
        direction=CallDirection.INBOUND,
        caller_phone="+1234567890"
    )
    await supervisor_service.create_active_call(db_session, call_data)

    stats = await supervisor_service.get_dashboard_stats(db_session)

    assert "active_calls" in stats
    assert "agents_available" in stats
    assert "agents_on_call" in stats
    assert "queue_waiting" in stats
    assert "active_alerts" in stats
    assert stats["active_calls"] >= 1
