"""Agents router - FastAPI"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.models.agent import Agent, AgentStatus
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentStatusUpdate

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/", response_model=list[AgentResponse])
async def list_agents(
    status_filter: AgentStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List agents with filtering

    Args:
        status_filter: Filter by agent status
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session

    Returns:
        List of agents
    """
    query = select(Agent)

    if status_filter:
        query = query.where(Agent.status == status_filter)

    query = query.offset(skip).limit(limit).order_by(Agent.created_at.desc())

    result = await db.execute(query)
    agents = result.scalars().all()
    return agents


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new agent

    Args:
        agent_data: Agent creation data
        db: Database session

    Returns:
        Created agent
    """
    from uuid import uuid4

    # Check if user already has an agent
    result = await db.execute(
        select(Agent).where(Agent.user_id == agent_data.user_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an agent profile"
        )

    agent = Agent(
        id=str(uuid4()),
        **agent_data.model_dump()
    )

    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get agent by ID

    Args:
        agent_id: Agent ID
        db: Database session

    Returns:
        Agent details
    """
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update agent

    Args:
        agent_id: Agent ID
        agent_data: Agent update data
        db: Database session

    Returns:
        Updated agent
    """
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Update fields
    for field, value in agent_data.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)

    return agent


@router.patch("/{agent_id}/status", response_model=AgentResponse)
async def update_agent_status(
    agent_id: str,
    status_data: AgentStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Quick update of agent status

    Args:
        agent_id: Agent ID
        status_data: New status
        db: Database session

    Returns:
        Updated agent
    """
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    agent.status = status_data.status

    await db.commit()
    await db.refresh(agent)

    return agent


@router.get("/available/count")
async def get_available_agents_count(
    db: AsyncSession = Depends(get_db)
):
    """
    Get count of available agents

    Args:
        db: Database session

    Returns:
        Count of available agents
    """
    from sqlalchemy import func

    result = await db.execute(
        select(func.count(Agent.id))
        .where(Agent.status == AgentStatus.AVAILABLE)
        .where(Agent.current_load < Agent.max_capacity)
    )
    count = result.scalar()

    return {"available_agents": count}
