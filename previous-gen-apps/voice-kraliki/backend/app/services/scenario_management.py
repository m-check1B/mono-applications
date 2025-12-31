"""Scenario management service for CRUD operations."""

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.scenario import (
    Scenario,
    ScenarioCreate,
    ScenarioNode,
    ScenarioNodeCreate,
    ScenarioNodeUpdate,
    ScenarioOption,
    ScenarioUpdate,
)


class ScenarioManagementService:
    """Service for managing scenarios, nodes, and options."""

    # ===== Scenario Operations =====

    async def create_scenario(
        self,
        db: AsyncSession,
        scenario_data: ScenarioCreate
    ) -> Scenario:
        """Create a new scenario."""
        db_scenario = Scenario(**scenario_data.model_dump())
        db.add(db_scenario)
        await db.commit()
        await db.refresh(db_scenario)
        return db_scenario

    async def get_scenario(
        self,
        db: AsyncSession,
        scenario_id: int,
        include_nodes: bool = False
    ) -> Scenario | None:
        """Get a scenario by ID with optional nodes."""
        query = select(Scenario).where(Scenario.id == scenario_id)

        if include_nodes:
            query = query.options(selectinload(Scenario.nodes).selectinload(ScenarioNode.options))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_scenarios(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        is_active: bool | None = None
    ) -> list[Scenario]:
        """Get all scenarios with optional filtering."""
        query = select(Scenario)

        if category:
            query = query.where(Scenario.category == category)
        if is_active is not None:
            query = query.where(Scenario.is_active == is_active)

        query = query.offset(skip).limit(limit).order_by(Scenario.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_scenario(
        self,
        db: AsyncSession,
        scenario_id: int,
        scenario_data: ScenarioUpdate
    ) -> Scenario | None:
        """Update a scenario."""
        update_data = scenario_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_scenario(db, scenario_id)

        query = (
            update(Scenario)
            .where(Scenario.id == scenario_id)
            .values(**update_data)
            .returning(Scenario)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def delete_scenario(
        self,
        db: AsyncSession,
        scenario_id: int
    ) -> bool:
        """Delete a scenario and all related data."""
        query = delete(Scenario).where(Scenario.id == scenario_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0

    # ===== Scenario Node Operations =====

    async def create_node(
        self,
        db: AsyncSession,
        node_data: ScenarioNodeCreate
    ) -> ScenarioNode:
        """Create a new scenario node."""
        data = node_data.model_dump()
        options_data = data.pop('options', [])

        db_node = ScenarioNode(**data)
        db.add(db_node)
        await db.flush() # Get ID

        for opt in options_data:
            db_opt = ScenarioOption(node_id=db_node.id, **opt)
            db.add(db_opt)

        await db.commit()
        await db.refresh(db_node)
        return db_node

    async def get_nodes_for_scenario(
        self,
        db: AsyncSession,
        scenario_id: int
    ) -> list[ScenarioNode]:
        """Get all nodes for a scenario."""
        query = select(ScenarioNode).where(
            ScenarioNode.scenario_id == scenario_id
        ).options(selectinload(ScenarioNode.options))

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_node(
        self,
        db: AsyncSession,
        node_id: int
    ) -> ScenarioNode | None:
        """Get a specific node."""
        query = select(ScenarioNode).where(
            ScenarioNode.id == node_id
        ).options(selectinload(ScenarioNode.options))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_node(
        self,
        db: AsyncSession,
        node_id: int,
        node_data: ScenarioNodeUpdate
    ) -> ScenarioNode | None:
        """Update a scenario node."""
        data = node_data.model_dump(exclude_unset=True)
        options_data = data.pop('options', None)

        if data:
            await db.execute(
                update(ScenarioNode)
                .where(ScenarioNode.id == node_id)
                .values(**data)
            )

        if options_data is not None:
            # Simple approach: delete existing options and recreate
            await db.execute(delete(ScenarioOption).where(ScenarioOption.node_id == node_id))
            for opt in options_data:
                db_opt = ScenarioOption(node_id=node_id, **opt)
                db.add(db_opt)

        await db.commit()
        return await self.get_node(db, node_id)

    async def delete_node(
        self,
        db: AsyncSession,
        node_id: int
    ) -> bool:
        """Delete a node."""
        query = delete(ScenarioNode).where(ScenarioNode.id == node_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0


# Singleton instance
_scenario_service: ScenarioManagementService | None = None


def get_scenario_service() -> ScenarioManagementService:
    """Get the scenario management service instance."""
    global _scenario_service
    if _scenario_service is None:
        _scenario_service = ScenarioManagementService()
    return _scenario_service
