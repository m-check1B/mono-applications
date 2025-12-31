"""Supervisor cockpit service for real-time monitoring and call management."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.supervisor import (
    ActiveCall,
    ActiveCallCreate,
    ActiveCallStatus,
    ActiveCallUpdate,
    AlertSeverity,
    CallQueue,
    CallQueueCreate,
    CallQueueStatus,
    CallQueueUpdate,
    InterventionType,
    PerformanceAlertCreate,
    SupervisorIntervention,
    SupervisorInterventionCreate,
)
from app.models.supervisor import SupervisorPerformanceAlert as PerformanceAlert
from app.models.team import AgentProfile, AgentStatus


class SupervisorService:
    """Service for supervisor cockpit operations."""

    # ===== Call Queue Management =====

    async def add_to_queue(
        self,
        db: AsyncSession,
        queue_data: CallQueueCreate
    ) -> CallQueue:
        """Add a call to the queue."""
        # Calculate queue position
        result = await db.execute(
            select(func.count(CallQueue.id)).where(
                CallQueue.status == CallQueueStatus.WAITING
            )
        )
        queue_position = result.scalar() + 1

        queue_entry = CallQueue(
            **queue_data.model_dump(),
            queue_position=queue_position,
            status=CallQueueStatus.WAITING
        )
        db.add(queue_entry)
        await db.commit()
        await db.refresh(queue_entry)

        return queue_entry

    async def get_queue_entries(
        self,
        db: AsyncSession,
        team_id: int | None = None,
        status: CallQueueStatus | None = None,
        limit: int = 100
    ) -> list[CallQueue]:
        """Get call queue entries with optional filters."""
        query = select(CallQueue).options(
            selectinload(CallQueue.assigned_agent)
        )

        filters = []
        if team_id:
            filters.append(CallQueue.team_id == team_id)
        if status:
            filters.append(CallQueue.status == status)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(CallQueue.priority.desc(), CallQueue.queued_at).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_queue_entry(
        self,
        db: AsyncSession,
        queue_id: int,
        update_data: CallQueueUpdate
    ) -> CallQueue | None:
        """Update a queue entry."""
        result = await db.execute(
            select(CallQueue).where(CallQueue.id == queue_id)
        )
        queue_entry = result.scalar_one_or_none()

        if not queue_entry:
            return None

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(queue_entry, field, value)

        # Update timestamps based on status
        if update_data.status:
            if update_data.status == CallQueueStatus.ASSIGNED:
                queue_entry.assigned_at = datetime.now(UTC)
            elif update_data.status == CallQueueStatus.ANSWERED:
                queue_entry.answered_at = datetime.now(UTC)
            elif update_data.status == CallQueueStatus.ABANDONED:
                queue_entry.abandoned_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(queue_entry)
        return queue_entry

    async def assign_to_agent(
        self,
        db: AsyncSession,
        queue_id: int,
        agent_id: int
    ) -> CallQueue | None:
        """Assign a queued call to an agent."""
        update_data = CallQueueUpdate(
            status=CallQueueStatus.ASSIGNED,
            assigned_agent_id=agent_id
        )
        return await self.update_queue_entry(db, queue_id, update_data)

    async def get_queue_statistics(
        self,
        db: AsyncSession,
        team_id: int | None = None
    ) -> dict[str, Any]:
        """Get queue statistics."""
        filters = []
        if team_id:
            filters.append(CallQueue.team_id == team_id)

        # Current waiting
        waiting_query = select(func.count(CallQueue.id)).where(
            and_(CallQueue.status == CallQueueStatus.WAITING, *filters)
        )
        result = await db.execute(waiting_query)
        waiting_count = result.scalar() or 0

        # Average wait time (last hour)
        hour_ago = datetime.now(UTC) - timedelta(hours=1)
        avg_wait_query = select(
            func.avg(
                func.extract('epoch', CallQueue.answered_at - CallQueue.queued_at)
            )
        ).where(
            and_(
                CallQueue.answered_at.isnot(None),
                CallQueue.queued_at >= hour_ago,
                *filters
            )
        )
        result = await db.execute(avg_wait_query)
        avg_wait_seconds = result.scalar() or 0

        # Abandoned calls (last hour)
        abandoned_query = select(func.count(CallQueue.id)).where(
            and_(
                CallQueue.status == CallQueueStatus.ABANDONED,
                CallQueue.queued_at >= hour_ago,
                *filters
            )
        )
        result = await db.execute(abandoned_query)
        abandoned_count = result.scalar() or 0

        # Total calls (last hour)
        total_query = select(func.count(CallQueue.id)).where(
            and_(CallQueue.queued_at >= hour_ago, *filters)
        )
        result = await db.execute(total_query)
        total_count = result.scalar() or 0

        abandon_rate = (abandoned_count / total_count * 100) if total_count > 0 else 0

        return {
            "waiting_count": waiting_count,
            "average_wait_seconds": int(avg_wait_seconds),
            "abandoned_count": abandoned_count,
            "abandon_rate_percentage": round(abandon_rate, 2),
            "total_calls_last_hour": total_count
        }

    # ===== Active Call Management =====

    async def create_active_call(
        self,
        db: AsyncSession,
        call_data: ActiveCallCreate
    ) -> ActiveCall:
        """Create an active call record."""
        call = ActiveCall(**call_data.model_dump())
        db.add(call)
        await db.commit()
        await db.refresh(call)
        return call

    async def get_active_calls(
        self,
        db: AsyncSession,
        team_id: int | None = None,
        agent_id: int | None = None,
        status: ActiveCallStatus | None = None
    ) -> list[ActiveCall]:
        """Get active calls with optional filters."""
        query = select(ActiveCall).options(
            selectinload(ActiveCall.agent),
            selectinload(ActiveCall.monitored_by)
        )

        filters = []
        if team_id:
            filters.append(ActiveCall.team_id == team_id)
        if agent_id:
            filters.append(ActiveCall.agent_id == agent_id)
        if status:
            filters.append(ActiveCall.status == status)
        else:
            # By default, exclude completed/failed calls
            filters.append(
                ActiveCall.status.not_in([ActiveCallStatus.COMPLETED, ActiveCallStatus.FAILED])
            )

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(ActiveCall.started_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_active_call(
        self,
        db: AsyncSession,
        call_id: int
    ) -> ActiveCall | None:
        """Get a specific active call."""
        result = await db.execute(
            select(ActiveCall)
            .where(ActiveCall.id == call_id)
            .options(
                selectinload(ActiveCall.agent),
                selectinload(ActiveCall.monitored_by),
                selectinload(ActiveCall.interventions)
            )
        )
        return result.scalar_one_or_none()

    async def update_active_call(
        self,
        db: AsyncSession,
        call_id: int,
        update_data: ActiveCallUpdate
    ) -> ActiveCall | None:
        """Update an active call."""
        result = await db.execute(
            select(ActiveCall).where(ActiveCall.id == call_id)
        )
        call = result.scalar_one_or_none()

        if not call:
            return None

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(call, field, value)

        # Calculate duration if ended
        if update_data.ended_at and call.started_at:
            call.duration_seconds = int((update_data.ended_at - call.started_at).total_seconds())

        await db.commit()
        await db.refresh(call)
        return call

    async def get_call_by_sid(
        self,
        db: AsyncSession,
        call_sid: str
    ) -> ActiveCall | None:
        """Get active call by external call SID."""
        result = await db.execute(
            select(ActiveCall).where(ActiveCall.call_sid == call_sid)
        )
        return result.scalar_one_or_none()

    # ===== Agent Monitoring =====

    async def get_agent_live_status(
        self,
        db: AsyncSession,
        team_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Get live status of all agents."""
        query = select(AgentProfile).options(
            selectinload(AgentProfile.user),
            selectinload(AgentProfile.team)
        )

        if team_id:
            query = query.where(AgentProfile.team_id == team_id)

        result = await db.execute(query)
        agents = list(result.scalars().all())

        # Get active calls for each agent
        agent_statuses = []
        for agent in agents:
            active_calls_result = await db.execute(
                select(ActiveCall)
                .where(
                    and_(
                        ActiveCall.agent_id == agent.id,
                        ActiveCall.status.not_in([ActiveCallStatus.COMPLETED, ActiveCallStatus.FAILED])
                    )
                )
            )
            active_calls = list(active_calls_result.scalars().all())

            agent_statuses.append({
                "agent_id": agent.id,
                "display_name": agent.display_name,
                "current_status": agent.current_status,
                "status_since": agent.status_since,
                "active_calls_count": len(active_calls),
                "active_calls": [
                    {
                        "id": call.id,
                        "call_sid": call.call_sid,
                        "direction": call.direction,
                        "status": call.status,
                        "duration_seconds": int((datetime.now(UTC) - call.started_at).total_seconds()),
                        "is_on_hold": call.is_on_hold
                    }
                    for call in active_calls
                ],
                "is_available": agent.available_for_calls,
                "max_concurrent_calls": agent.max_concurrent_calls
            })

        return agent_statuses

    # ===== Supervisor Interventions =====

    async def start_intervention(
        self,
        db: AsyncSession,
        intervention_data: SupervisorInterventionCreate,
        supervisor_id: int
    ) -> SupervisorIntervention:
        """Start a supervisor intervention on a call."""
        # Get the call to get agent_id
        result = await db.execute(
            select(ActiveCall).where(ActiveCall.id == intervention_data.call_id)
        )
        call = result.scalar_one_or_none()

        if not call:
            raise ValueError("Call not found")

        intervention = SupervisorIntervention(
            **intervention_data.model_dump(),
            supervisor_id=supervisor_id,
            agent_id=call.agent_id
        )
        db.add(intervention)

        # Update call monitoring status
        if intervention_data.intervention_type in [InterventionType.MONITOR, InterventionType.WHISPER]:
            call.is_being_monitored = True
            call.monitored_by_id = supervisor_id

        await db.commit()
        await db.refresh(intervention)
        return intervention

    async def end_intervention(
        self,
        db: AsyncSession,
        intervention_id: int
    ) -> SupervisorIntervention | None:
        """End a supervisor intervention."""
        result = await db.execute(
            select(SupervisorIntervention).where(SupervisorIntervention.id == intervention_id)
        )
        intervention = result.scalar_one_or_none()

        if not intervention or intervention.ended_at:
            return None

        intervention.ended_at = datetime.now(UTC)
        intervention.duration_seconds = int(
            (intervention.ended_at - intervention.started_at).total_seconds()
        )

        # Update call monitoring status
        call_result = await db.execute(
            select(ActiveCall).where(ActiveCall.id == intervention.call_id)
        )
        call = call_result.scalar_one_or_none()
        if call:
            call.is_being_monitored = False
            call.monitored_by_id = None

        await db.commit()
        await db.refresh(intervention)
        return intervention

    async def get_interventions(
        self,
        db: AsyncSession,
        supervisor_id: int | None = None,
        agent_id: int | None = None,
        call_id: int | None = None,
        limit: int = 100
    ) -> list[SupervisorIntervention]:
        """Get supervisor interventions with filters."""
        query = select(SupervisorIntervention).options(
            selectinload(SupervisorIntervention.supervisor),
            selectinload(SupervisorIntervention.agent)
        )

        filters = []
        if supervisor_id:
            filters.append(SupervisorIntervention.supervisor_id == supervisor_id)
        if agent_id:
            filters.append(SupervisorIntervention.agent_id == agent_id)
        if call_id:
            filters.append(SupervisorIntervention.call_id == call_id)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(desc(SupervisorIntervention.started_at)).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    # ===== Performance Alerts =====

    async def create_alert(
        self,
        db: AsyncSession,
        alert_data: PerformanceAlertCreate
    ) -> PerformanceAlert:
        """Create a performance alert."""
        alert = PerformanceAlert(**alert_data.model_dump())
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def get_active_alerts(
        self,
        db: AsyncSession,
        team_id: int | None = None,
        agent_id: int | None = None,
        severity: AlertSeverity | None = None
    ) -> list[PerformanceAlert]:
        """Get active performance alerts."""
        query = select(PerformanceAlert).options(
            selectinload(PerformanceAlert.team),
            selectinload(PerformanceAlert.agent),
            selectinload(PerformanceAlert.acknowledged_by)
        )

        filters = [PerformanceAlert.is_active == True]

        if team_id:
            filters.append(PerformanceAlert.team_id == team_id)
        if agent_id:
            filters.append(PerformanceAlert.agent_id == agent_id)
        if severity:
            filters.append(PerformanceAlert.severity == severity)

        query = query.where(and_(*filters)).order_by(
            PerformanceAlert.severity.desc(),
            PerformanceAlert.created_at.desc()
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def acknowledge_alert(
        self,
        db: AsyncSession,
        alert_id: int,
        user_id: int
    ) -> PerformanceAlert | None:
        """Acknowledge a performance alert."""
        result = await db.execute(
            select(PerformanceAlert).where(PerformanceAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        alert.is_acknowledged = True
        alert.acknowledged_at = datetime.now(UTC)
        alert.acknowledged_by_id = user_id

        await db.commit()
        await db.refresh(alert)
        return alert

    async def resolve_alert(
        self,
        db: AsyncSession,
        alert_id: int,
        resolution_notes: str | None = None
    ) -> PerformanceAlert | None:
        """Resolve a performance alert."""
        result = await db.execute(
            select(PerformanceAlert).where(PerformanceAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        alert.is_resolved = True
        alert.is_active = False
        alert.resolved_at = datetime.now(UTC)
        if resolution_notes:
            alert.resolution_notes = resolution_notes

        await db.commit()
        await db.refresh(alert)
        return alert

    # ===== Dashboard Analytics =====

    async def get_dashboard_stats(
        self,
        db: AsyncSession,
        team_id: int | None = None
    ) -> dict[str, Any]:
        """Get real-time dashboard statistics."""
        filters = []
        if team_id:
            filters.append(ActiveCall.team_id == team_id)

        # Active calls count
        active_calls_query = select(func.count(ActiveCall.id)).where(
            and_(
                ActiveCall.status.not_in([ActiveCallStatus.COMPLETED, ActiveCallStatus.FAILED]),
                *filters
            )
        )
        result = await db.execute(active_calls_query)
        active_calls = result.scalar() or 0

        # Agents by status
        agent_filters = []
        if team_id:
            agent_filters.append(AgentProfile.team_id == team_id)

        agent_status_query = select(
            AgentProfile.current_status,
            func.count(AgentProfile.id)
        ).where(*agent_filters).group_by(AgentProfile.current_status)

        result = await db.execute(agent_status_query)
        agent_statuses = {row[0]: row[1] for row in result.all()}

        # Queue stats
        queue_stats = await self.get_queue_statistics(db, team_id)

        # Active alerts count
        alert_filters = [PerformanceAlert.is_active == True]
        if team_id:
            alert_filters.append(PerformanceAlert.team_id == team_id)

        alerts_query = select(func.count(PerformanceAlert.id)).where(and_(*alert_filters))
        result = await db.execute(alerts_query)
        active_alerts = result.scalar() or 0

        return {
            "active_calls": active_calls,
            "agents_available": agent_statuses.get(AgentStatus.AVAILABLE, 0),
            "agents_on_call": agent_statuses.get(AgentStatus.ON_CALL, 0),
            "agents_on_break": agent_statuses.get(AgentStatus.BREAK, 0),
            "agents_offline": agent_statuses.get(AgentStatus.OFFLINE, 0),
            "queue_waiting": queue_stats["waiting_count"],
            "average_wait_time": queue_stats["average_wait_seconds"],
            "abandon_rate": queue_stats["abandon_rate_percentage"],
            "active_alerts": active_alerts,
            "timestamp": datetime.now(UTC)
        }
