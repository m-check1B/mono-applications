"""Team and agent management service."""

from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.shift import (
    AgentPerformance,
    Shift,
    ShiftCreate,
    ShiftStatus,
    ShiftUpdate,
    TeamPerformance,
)
from app.models.team import (
    AgentProfile,
    AgentProfileCreate,
    AgentProfileUpdate,
    AgentStatus,
    Team,
    TeamCreate,
    TeamMember,
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamRole,
    TeamUpdate,
)


class TeamManagementService:
    """Service for managing teams, agents, and shifts."""

    # ===== Team Operations =====

    async def create_team(
        self,
        db: AsyncSession,
        team_data: TeamCreate
    ) -> Team:
        """Create a new team."""
        db_team = Team(**team_data.model_dump())
        db.add(db_team)
        await db.commit()
        await db.refresh(db_team)
        return db_team

    async def get_team(
        self,
        db: AsyncSession,
        team_id: int,
        include_members: bool = False
    ) -> Team | None:
        """Get a team by ID."""
        query = select(Team).where(Team.id == team_id)

        if include_members:
            query = query.options(selectinload(Team.team_members))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_teams(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        parent_team_id: int | None = None,
        is_active: bool | None = None
    ) -> list[Team]:
        """Get all teams with optional filtering."""
        query = select(Team)

        if parent_team_id is not None:
            query = query.where(Team.parent_team_id == parent_team_id)
        if is_active is not None:
            query = query.where(Team.is_active == is_active)

        query = query.offset(skip).limit(limit).order_by(Team.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_team_hierarchy(
        self,
        db: AsyncSession,
        root_team_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Get team hierarchy as nested structure."""
        # Get all teams
        query = select(Team).where(Team.is_active == True)
        if root_team_id:
            # Get team and its children recursively (simplified version)
            query = query.where(
                or_(
                    Team.id == root_team_id,
                    Team.parent_team_id == root_team_id
                )
            )

        result = await db.execute(query)
        teams = list(result.scalars().all())

        # Build hierarchy
        team_map = {team.id: {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "manager_id": team.manager_id,
            "total_agents": team.total_agents,
            "active_agents": team.active_agents,
            "parent_team_id": team.parent_team_id,
            "children": []
        } for team in teams}

        # Organize into hierarchy
        root_teams = []
        for team_dict in team_map.values():
            if team_dict["parent_team_id"] is None or team_dict["parent_team_id"] not in team_map:
                root_teams.append(team_dict)
            else:
                parent = team_map[team_dict["parent_team_id"]]
                parent["children"].append(team_dict)

        return root_teams

    async def update_team(
        self,
        db: AsyncSession,
        team_id: int,
        team_data: TeamUpdate
    ) -> Team | None:
        """Update a team."""
        update_data = team_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_team(db, team_id)

        query = (
            update(Team)
            .where(Team.id == team_id)
            .values(**update_data)
            .returning(Team)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def delete_team(
        self,
        db: AsyncSession,
        team_id: int
    ) -> bool:
        """Delete a team."""
        query = delete(Team).where(Team.id == team_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0

    async def update_team_metrics(
        self,
        db: AsyncSession,
        team_id: int
    ) -> None:
        """Update team metrics based on members."""
        # Count total agents
        total_query = select(func.count(TeamMember.id)).where(
            TeamMember.team_id == team_id,
            TeamMember.is_active == True
        )
        total_agents = (await db.execute(total_query)).scalar() or 0

        # Count active agents (available status)
        active_query = select(func.count(AgentProfile.id)).select_from(TeamMember).join(
            AgentProfile, TeamMember.user_id == AgentProfile.user_id
        ).where(
            TeamMember.team_id == team_id,
            TeamMember.is_active == True,
            AgentProfile.is_available == True
        )
        active_agents = (await db.execute(active_query)).scalar() or 0

        # Update team
        await db.execute(
            update(Team)
            .where(Team.id == team_id)
            .values(
                total_agents=total_agents,
                active_agents=active_agents
            )
        )
        await db.commit()

    # ===== Team Member Operations =====

    async def add_team_member(
        self,
        db: AsyncSession,
        member_data: TeamMemberCreate
    ) -> TeamMember:
        """Add a member to a team."""
        db_member = TeamMember(**member_data.model_dump())
        db.add(db_member)
        await db.commit()
        await db.refresh(db_member)

        # Update team metrics
        await self.update_team_metrics(db, member_data.team_id)

        return db_member

    async def get_team_members(
        self,
        db: AsyncSession,
        team_id: int,
        role: TeamRole | None = None,
        is_active: bool | None = None
    ) -> list[TeamMember]:
        """Get team members with optional filtering."""
        query = select(TeamMember).where(TeamMember.team_id == team_id)

        if role:
            query = query.where(TeamMember.role == role)
        if is_active is not None:
            query = query.where(TeamMember.is_active == is_active)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_team_member(
        self,
        db: AsyncSession,
        member_id: int,
        member_data: TeamMemberUpdate
    ) -> TeamMember | None:
        """Update a team member."""
        update_data = member_data.model_dump(exclude_unset=True)
        if not update_data:
            query = select(TeamMember).where(TeamMember.id == member_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()

        query = (
            update(TeamMember)
            .where(TeamMember.id == member_id)
            .values(**update_data)
            .returning(TeamMember)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def remove_team_member(
        self,
        db: AsyncSession,
        member_id: int
    ) -> bool:
        """Remove a member from a team."""
        # Get member to update team metrics
        query = select(TeamMember).where(TeamMember.id == member_id)
        result = await db.execute(query)
        member = result.scalar_one_or_none()

        if not member:
            return False

        team_id = member.team_id

        # Delete member
        delete_query = delete(TeamMember).where(TeamMember.id == member_id)
        result = await db.execute(delete_query)
        await db.commit()

        if result.rowcount > 0:
            await self.update_team_metrics(db, team_id)
            return True
        return False

    # ===== Agent Profile Operations =====

    async def create_agent_profile(
        self,
        db: AsyncSession,
        profile_data: AgentProfileCreate
    ) -> AgentProfile:
        """Create an agent profile."""
        db_profile = AgentProfile(**profile_data.model_dump())
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)

        # Update team metrics if agent assigned to team
        if profile_data.team_id:
            await self.update_team_metrics(db, profile_data.team_id)

        return db_profile

    async def get_agent_profile(
        self,
        db: AsyncSession,
        agent_id: int
    ) -> AgentProfile | None:
        """Get an agent profile by ID."""
        query = select(AgentProfile).where(AgentProfile.id == agent_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_agent_profile_by_user_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> AgentProfile | None:
        """Get an agent profile by user ID."""
        query = select(AgentProfile).where(AgentProfile.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_agents(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        team_id: int | None = None,
        status: AgentStatus | None = None,
        is_available: bool | None = None
    ) -> list[AgentProfile]:
        """Get agent profiles with optional filtering."""
        query = select(AgentProfile)

        if team_id is not None:
            query = query.where(AgentProfile.team_id == team_id)
        if status:
            query = query.where(AgentProfile.current_status == status)
        if is_available is not None:
            query = query.where(AgentProfile.is_available == is_available)

        query = query.offset(skip).limit(limit).order_by(AgentProfile.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_agent_profile(
        self,
        db: AsyncSession,
        agent_id: int,
        profile_data: AgentProfileUpdate
    ) -> AgentProfile | None:
        """Update an agent profile."""
        update_data = profile_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_agent_profile(db, agent_id)

        # Track if status changed
        if "current_status" in update_data:
            update_data["status_since"] = datetime.now(UTC)

        # Update last activity
        update_data["last_activity_at"] = datetime.now(UTC)

        query = (
            update(AgentProfile)
            .where(AgentProfile.id == agent_id)
            .values(**update_data)
            .returning(AgentProfile)
        )
        result = await db.execute(query)
        await db.commit()

        updated_profile = result.scalar_one_or_none()

        # Update team metrics if team changed
        if updated_profile and "team_id" in update_data:
            if update_data["team_id"]:
                await self.update_team_metrics(db, update_data["team_id"])

        return updated_profile

    async def assign_agent_to_team(
        self,
        db: AsyncSession,
        agent_id: int,
        team_id: int,
        role: TeamRole = TeamRole.AGENT
    ) -> AgentProfile | None:
        """Assign an agent to a team."""
        # Get agent
        agent = await self.get_agent_profile(db, agent_id)
        if not agent:
            return None

        # Update agent team
        profile_data = AgentProfileUpdate(team_id=team_id)
        updated_agent = await self.update_agent_profile(db, agent_id, profile_data)

        # Add team member entry
        member_data = TeamMemberCreate(
            team_id=team_id,
            user_id=agent.user_id,
            role=role
        )
        await self.add_team_member(db, member_data)

        return updated_agent

    # ===== Shift Operations =====

    async def create_shift(
        self,
        db: AsyncSession,
        shift_data: ShiftCreate
    ) -> Shift:
        """Create a shift."""
        db_shift = Shift(**shift_data.model_dump())
        db.add(db_shift)
        await db.commit()
        await db.refresh(db_shift)
        return db_shift

    async def get_shift(
        self,
        db: AsyncSession,
        shift_id: int
    ) -> Shift | None:
        """Get a shift by ID."""
        query = select(Shift).where(Shift.id == shift_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_shifts(
        self,
        db: AsyncSession,
        agent_id: int | None = None,
        team_id: int | None = None,
        shift_date: date | None = None,
        status: ShiftStatus | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Shift]:
        """Get shifts with optional filtering."""
        query = select(Shift)

        if agent_id:
            query = query.where(Shift.agent_id == agent_id)
        if team_id:
            query = query.where(Shift.team_id == team_id)
        if shift_date:
            query = query.where(Shift.shift_date == shift_date)
        if status:
            query = query.where(Shift.status == status)

        query = query.offset(skip).limit(limit).order_by(Shift.shift_date.desc(), Shift.start_time)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_shift(
        self,
        db: AsyncSession,
        shift_id: int,
        shift_data: ShiftUpdate
    ) -> Shift | None:
        """Update a shift."""
        update_data = shift_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_shift(db, shift_id)

        query = (
            update(Shift)
            .where(Shift.id == shift_id)
            .values(**update_data)
            .returning(Shift)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def clock_in(
        self,
        db: AsyncSession,
        shift_id: int
    ) -> Shift | None:
        """Clock in for a shift."""
        now = datetime.now(UTC)
        return await self.update_shift(
            db,
            shift_id,
            ShiftUpdate(
                clock_in_time=now,
                actual_start_time=now,
                status=ShiftStatus.IN_PROGRESS
            )
        )

    async def clock_out(
        self,
        db: AsyncSession,
        shift_id: int
    ) -> Shift | None:
        """Clock out from a shift."""
        now = datetime.now(UTC)
        return await self.update_shift(
            db,
            shift_id,
            ShiftUpdate(
                clock_out_time=now,
                actual_end_time=now,
                status=ShiftStatus.COMPLETED
            )
        )

    # ===== Performance Operations =====

    async def get_agent_performance(
        self,
        db: AsyncSession,
        agent_id: int,
        period_date: date,
        period_type: str = "daily"
    ) -> AgentPerformance | None:
        """Get agent performance for a period."""
        query = select(AgentPerformance).where(
            and_(
                AgentPerformance.agent_id == agent_id,
                AgentPerformance.period_date == period_date,
                AgentPerformance.period_type == period_type
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_team_performance(
        self,
        db: AsyncSession,
        team_id: int,
        period_date: date,
        period_type: str = "daily"
    ) -> TeamPerformance | None:
        """Get team performance for a period."""
        query = select(TeamPerformance).where(
            and_(
                TeamPerformance.team_id == team_id,
                TeamPerformance.period_date == period_date,
                TeamPerformance.period_type == period_type
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


# Singleton instance
_team_service: TeamManagementService | None = None


def get_team_service() -> TeamManagementService:
    """Get the team management service instance."""
    global _team_service
    if _team_service is None:
        _team_service = TeamManagementService()
    return _team_service
