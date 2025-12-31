"""
Queue Routing Service

Implements advanced call routing strategies for queue management.
"""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_state import CallState, CallStatus
from app.models.queue_config import QueueConfig, RoutingStrategy
from app.models.supervisor import CallQueue, CallQueueStatus
from app.models.team import AgentProfile, AgentStatus

logger = logging.getLogger(__name__)


class QueueRoutingService:
    """Service for intelligent call routing in queues."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def route_call_to_agent(
        self,
        db: AsyncSession,
        queue_entry: CallQueue,
        queue_config: QueueConfig | None = None
    ) -> AgentProfile | None:
        """
        Route a call from queue to the best available agent.

        Args:
            db: Database session
            queue_entry: Call queue entry to route
            queue_config: Queue configuration (optional)

        Returns:
            Best matching agent or None if no agent available
        """
        if not queue_config:
            # Get default queue config or use FIFO
            strategy = RoutingStrategy.FIFO
        else:
            strategy = queue_config.routing_strategy

        # Get available agents
        available_agents = await self._get_available_agents(
            db,
            team_id=queue_entry.team_id,
            required_skills=queue_entry.required_skills,
            required_language=queue_entry.required_language,
            skill_match_threshold=queue_config.skill_match_threshold if queue_config else 0.7
        )

        if not available_agents:
            self.logger.warning(f"No available agents for queue entry {queue_entry.id}")
            return None

        # Route based on strategy
        if strategy == RoutingStrategy.FIFO:
            return available_agents[0]  # First available

        elif strategy == RoutingStrategy.PRIORITY:
            return await self._route_by_priority(db, available_agents, queue_entry)

        elif strategy == RoutingStrategy.SKILL_BASED:
            return await self._route_by_skills(db, available_agents, queue_entry)

        elif strategy == RoutingStrategy.LONGEST_IDLE:
            return await self._route_by_longest_idle(db, available_agents)

        elif strategy == RoutingStrategy.ROUND_ROBIN:
            return await self._route_by_round_robin(db, available_agents, queue_entry.team_id)

        elif strategy == RoutingStrategy.LEAST_OCCUPIED:
            return await self._route_by_least_occupied(db, available_agents)

        else:
            # Default to first available
            return available_agents[0]

    async def _get_available_agents(
        self,
        db: AsyncSession,
        team_id: int | None = None,
        required_skills: list[str] | None = None,
        required_language: str | None = None,
        skill_match_threshold: float = 0.7
    ) -> list[AgentProfile]:
        """Get list of available agents matching criteria."""

        # Build query for available agents
        query = select(AgentProfile).where(
            and_(
                AgentProfile.current_status == AgentStatus.AVAILABLE,
                AgentProfile.is_active == True
            )
        )

        # Filter by team if specified
        if team_id:
            query = query.where(AgentProfile.team_id == team_id)

        # Execute query
        result = await db.execute(query)
        agents = list(result.scalars().all())

        # Filter by skills if required
        if required_skills and len(required_skills) > 0:
            agents = await self._filter_agents_by_skills(
                agents,
                required_skills,
                skill_match_threshold
            )

        # Filter by language if required
        if required_language:
            agents = [
                agent for agent in agents
                if required_language in (agent.languages or [])
            ]

        # Filter by concurrent call capacity
        agents = [
            agent for agent in agents
            if agent.active_calls_count < agent.max_concurrent_calls
        ]

        return agents

    async def _filter_agents_by_skills(
        self,
        agents: list[AgentProfile],
        required_skills: list[str],
        threshold: float
    ) -> list[AgentProfile]:
        """Filter agents by skill match percentage."""
        matched_agents = []

        for agent in agents:
            agent_skills = set(agent.skills or [])
            required_skills_set = set(required_skills)

            if not required_skills_set:
                matched_agents.append(agent)
                continue

            # Calculate match percentage
            matched_skills = agent_skills.intersection(required_skills_set)
            match_percentage = len(matched_skills) / len(required_skills_set)

            if match_percentage >= threshold:
                matched_agents.append(agent)

        return matched_agents

    async def _route_by_priority(
        self,
        db: AsyncSession,
        agents: list[AgentProfile],
        queue_entry: CallQueue
    ) -> AgentProfile:
        """Route based on agent priority/tier."""
        # Sort agents by tier (assuming higher tier = higher priority)
        # If no tier field, use agent_id as tiebreaker
        sorted_agents = sorted(
            agents,
            key=lambda a: (getattr(a, 'tier', 999), a.id)
        )
        return sorted_agents[0]

    async def _route_by_skills(
        self,
        db: AsyncSession,
        agents: list[AgentProfile],
        queue_entry: CallQueue
    ) -> AgentProfile:
        """Route to agent with best skill match."""
        if not queue_entry.required_skills:
            return agents[0]

        required_skills_set = set(queue_entry.required_skills)
        best_agent = agents[0]
        best_match_score = 0.0

        for agent in agents:
            agent_skills = set(agent.skills or [])

            # Calculate match score
            matched_skills = agent_skills.intersection(required_skills_set)
            match_score = len(matched_skills) / len(required_skills_set) if required_skills_set else 0

            # Bonus for extra relevant skills
            extra_skills_bonus = len(matched_skills) * 0.1
            total_score = match_score + extra_skills_bonus

            if total_score > best_match_score:
                best_match_score = total_score
                best_agent = agent

        return best_agent

    async def _route_by_longest_idle(
        self,
        db: AsyncSession,
        agents: list[AgentProfile]
    ) -> AgentProfile:
        """Route to agent who has been idle longest."""
        # Sort by status_since (oldest first)
        sorted_agents = sorted(
            agents,
            key=lambda a: a.status_since if a.status_since else datetime.now(UTC)
        )
        return sorted_agents[0]

    async def _route_by_round_robin(
        self,
        db: AsyncSession,
        agents: list[AgentProfile],
        team_id: int | None
    ) -> AgentProfile:
        """
        Route using round-robin distribution.

        Note: For true round-robin, we'd need to track last assignment.
        This is a simplified version using agent ID rotation.
        """
        # Simple round-robin based on current minute + agent count
        # More sophisticated would track last assignment in database
        current_minute = datetime.now(UTC).minute
        index = current_minute % len(agents)
        return agents[index]

    async def _route_by_least_occupied(
        self,
        db: AsyncSession,
        agents: list[AgentProfile]
    ) -> AgentProfile:
        """Route to agent with fewest active calls."""
        # Sort by active_calls_count (lowest first)
        sorted_agents = sorted(
            agents,
            key=lambda a: a.active_calls_count
        )
        return sorted_agents[0]

    async def calculate_estimated_wait_time(
        self,
        db: AsyncSession,
        queue_entry: CallQueue,
        queue_config: QueueConfig | None = None
    ) -> int:
        """
        Calculate estimated wait time for a queue entry in seconds.

        Args:
            db: Database session
            queue_entry: Call queue entry
            queue_config: Queue configuration

        Returns:
            Estimated wait time in seconds
        """
        # Get queue position
        position = queue_entry.queue_position or 0

        if position <= 0:
            return 0

        # Get average handle time for team/campaign
        avg_handle_time = await self._get_average_handle_time(
            db,
            team_id=queue_entry.team_id,
            campaign_id=queue_entry.campaign_id
        )

        # Get number of available agents
        available_agents = await self._get_available_agents(
            db,
            team_id=queue_entry.team_id
        )
        num_agents = len(available_agents)

        if num_agents == 0:
            # No agents available, use max wait time
            return queue_config.max_wait_time_seconds if queue_config else 300

        # Estimate: (position / agents) * avg_handle_time
        estimated_wait = int((position / num_agents) * avg_handle_time)

        # Cap at max wait time
        max_wait = queue_config.max_wait_time_seconds if queue_config else 300
        return min(estimated_wait, max_wait)

    async def _get_average_handle_time(
        self,
        db: AsyncSession,
        team_id: int | None = None,
        campaign_id: int | None = None
    ) -> float:
        """Get average handle time for recent calls (last 30 days)."""
        # Query completed calls to calculate average duration
        # We use ended_at - created_at as an approximation of handle time

        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)

        query = select(
            func.avg(
                func.extract('epoch', CallState.ended_at - CallState.created_at)
            )
        ).where(
            and_(
                CallState.status == CallStatus.COMPLETED,
                CallState.ended_at.isnot(None),
                CallState.created_at.isnot(None),
                CallState.created_at >= thirty_days_ago
            )
        )

        # Filter by team/campaign if metadata supports it
        # Note: call_custom_metadata stores team_id and campaign_id
        if team_id:
            # Using astext for PostgreSQL JSON compatibility
            query = query.where(
                CallState.call_custom_metadata["team_id"].astext == str(team_id)
            )

        if campaign_id:
            query = query.where(
                CallState.call_custom_metadata["campaign_id"].astext == str(campaign_id)
            )

        try:
            result = await db.execute(query)
            avg_time = result.scalar()

            if avg_time is not None:
                return float(avg_time)
        except Exception as e:
            self.logger.error(f"Error calculating average handle time: {e}")

        # Fallback to default of 180 seconds (3 minutes)
        return 180.0

    async def update_queue_positions(
        self,
        db: AsyncSession,
        team_id: int | None = None
    ) -> int:
        """
        Update queue positions for all waiting calls.

        Args:
            db: Database session
            team_id: Optional team filter

        Returns:
            Number of entries updated
        """
        # Get all waiting calls, ordered by priority and queued_at
        query = select(CallQueue).where(
            CallQueue.status == CallQueueStatus.WAITING
        )

        if team_id:
            query = query.where(CallQueue.team_id == team_id)

        query = query.order_by(
            CallQueue.priority.desc(),
            CallQueue.queued_at.asc()
        )

        result = await db.execute(query)
        entries = list(result.scalars().all())

        # Update positions
        for position, entry in enumerate(entries, start=1):
            entry.queue_position = position

        await db.commit()

        return len(entries)

    async def check_overflow_conditions(
        self,
        db: AsyncSession,
        queue_config: QueueConfig
    ) -> bool:
        """
        Check if overflow conditions are met.

        Args:
            db: Database session
            queue_config: Queue configuration

        Returns:
            True if should overflow to another queue
        """
        if not queue_config.overflow_enabled or not queue_config.overflow_queue_id:
            return False

        # Count waiting calls in queue
        query = select(func.count(CallQueue.id)).where(
            and_(
                CallQueue.status == CallQueueStatus.WAITING,
                or_(
                    CallQueue.team_id == queue_config.team_id,
                    CallQueue.campaign_id == queue_config.campaign_id
                )
            )
        )

        result = await db.execute(query)
        waiting_count = result.scalar() or 0

        # Check if over threshold
        return waiting_count >= queue_config.overflow_threshold
