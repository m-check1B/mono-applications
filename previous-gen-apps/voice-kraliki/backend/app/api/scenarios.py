"""Scenario management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_auth import require_user
from app.database import get_db
from app.models.scenario import (
    ScenarioCreate,
    ScenarioNodeCreate,
    ScenarioNodeResponse,
    ScenarioNodeUpdate,
    ScenarioOptionCreate,
    ScenarioResponse,
    ScenarioUpdate,
)
from app.models.user import User
from app.services.scenario_management import get_scenario_service
from app.services.scenario_templates import get_all_templates, get_template_by_id

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


class TemplateInfo(BaseModel):
    """Template summary for listing."""
    id: str
    name: str
    description: str
    category: str
    difficulty: str


class CreateFromTemplateRequest(BaseModel):
    """Request to create scenario from template."""
    template_id: str


@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    scenario_data: ScenarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Create a new training scenario."""
    service = get_scenario_service()
    return await service.create_scenario(db, scenario_data)


@router.get("", response_model=list[ScenarioResponse])
async def list_scenarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """List all scenarios."""
    service = get_scenario_service()
    return await service.get_scenarios(db, skip=skip, limit=limit, category=category)


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get a specific scenario."""
    service = get_scenario_service()
    scenario = await service.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: int,
    scenario_data: ScenarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Update a scenario."""
    service = get_scenario_service()
    scenario = await service.update_scenario(db, scenario_id, scenario_data)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Delete a scenario."""
    service = get_scenario_service()
    if not await service.delete_scenario(db, scenario_id):
        raise HTTPException(status_code=404, detail="Scenario not found")


# ===== Node Endpoints =====

@router.post("/nodes", response_model=ScenarioNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    node_data: ScenarioNodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Create a new node in a scenario."""
    service = get_scenario_service()
    return await service.create_node(db, node_data)


@router.get("/{scenario_id}/nodes", response_model=list[ScenarioNodeResponse])
async def list_scenario_nodes(
    scenario_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """List all nodes for a scenario."""
    service = get_scenario_service()
    return await service.get_nodes_for_scenario(db, scenario_id)


@router.get("/nodes/{node_id}", response_model=ScenarioNodeResponse)
async def get_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Get a specific node."""
    service = get_scenario_service()
    node = await service.get_node(db, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.put("/nodes/{node_id}", response_model=ScenarioNodeResponse)
async def update_node(
    node_id: int,
    node_data: ScenarioNodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Update a node."""
    service = get_scenario_service()
    node = await service.update_node(db, node_id, node_data)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Delete a node."""
    service = get_scenario_service()
    if not await service.delete_node(db, node_id):
        raise HTTPException(status_code=404, detail="Node not found")


# ===== Template Endpoints =====

@router.get("/templates/list", response_model=list[TemplateInfo])
async def list_templates(
    current_user: User = Depends(require_user)
):
    """List all available scenario templates."""
    templates = get_all_templates()
    return [
        TemplateInfo(
            id=t["id"],
            name=t["name"],
            description=t["scenario"]["description"],
            category=t["scenario"]["category"],
            difficulty=t["scenario"]["difficulty"],
        )
        for t in templates
    ]


@router.post("/templates/create", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_from_template(
    request: CreateFromTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    """Create a new scenario from a pre-built template.

    Available templates:
    - angry_customer: Practice de-escalation with an upset customer
    - curious_learner: Practice consultative selling with an interested prospect
    """
    template = get_template_by_id(request.template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{request.template_id}' not found. Available: angry_customer, curious_learner"
        )

    service = get_scenario_service()

    # Create the scenario
    scenario_data = ScenarioCreate(**template["scenario"])
    scenario = await service.create_scenario(db, scenario_data)

    # Create all nodes first (without connections) to get their IDs
    node_id_map: dict[int, int] = {}  # Maps template index to real node ID
    created_nodes = []

    for idx, node_def in enumerate(template["nodes"]):
        node_create = ScenarioNodeCreate(
            scenario_id=scenario.id,
            node_type=node_def["node_type"],
            name=node_def["name"],
            text_content=node_def.get("text_content"),
            next_node_id=None,  # Set later after all nodes exist
            condition_expression=node_def.get("condition_expression"),
            variable_name=node_def.get("variable_name"),
            variable_value=node_def.get("variable_value"),
            options=[],  # Set later after all nodes exist
        )
        created_node = await service.create_node(db, node_create)
        node_id_map[idx] = created_node.id
        created_nodes.append((idx, node_def, created_node))

    # Update nodes with proper connections
    for idx, node_def, created_node in created_nodes:
        # Resolve next_node_id
        next_idx = node_def.get("next_index")
        next_node_id = node_id_map.get(next_idx) if next_idx is not None else None

        # Resolve options
        options = []
        for opt in node_def.get("options", []):
            opt_next_idx = opt.get("next_index")
            opt_next_id = node_id_map.get(opt_next_idx) if opt_next_idx is not None else None
            options.append(ScenarioOptionCreate(
                label=opt["label"],
                next_node_id=opt_next_id,
            ))

        # Update the node
        node_update = ScenarioNodeUpdate(
            node_type=node_def["node_type"],
            name=node_def["name"],
            text_content=node_def.get("text_content"),
            next_node_id=next_node_id,
            condition_expression=node_def.get("condition_expression"),
            variable_name=node_def.get("variable_name"),
            variable_value=node_def.get("variable_value"),
            options=options,
        )
        await service.update_node(db, created_node.id, node_update)

    # Set the entry node
    entry_node_name = template.get("entry_node_name")
    if entry_node_name:
        for idx, node_def, _ in created_nodes:
            if node_def["name"] == entry_node_name:
                scenario.entry_node_id = node_id_map[idx]
                break

        # Update scenario with entry node
        await service.update_scenario(
            db, scenario.id,
            ScenarioUpdate(entry_node_id=scenario.entry_node_id)
        )

    return scenario
