"""Call Routing API endpoints."""

from datetime import datetime

from app.auth.jwt_auth import get_current_user
from app.database import get_db
from app.models.routing import (
    RouteCallRequest,
    RouteCallResponse,
    RoutingLogResponse,
    RoutingRuleCreate,
    RoutingRuleResponse,
    RoutingRuleUpdate,
    RoutingTargetCreate,
    RoutingTargetResponse,
)
from app.models.user import User
from app.services.routing import RoutingError, RoutingService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


# ===== Rule Management =====

@router.post("/rules", response_model=RoutingRuleResponse, status_code=status.HTTP_201_CREATED)
def create_routing_rule(
    rule_data: RoutingRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new routing rule."""
    service = RoutingService(db)

    try:
        rule = service.create_rule(rule_data)
        return rule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create routing rule: {str(e)}"
        )


@router.get("/rules", response_model=list[RoutingRuleResponse])
def list_routing_rules(
    campaign_id: int | None = Query(None),
    team_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all routing rules with optional filters."""
    service = RoutingService(db)

    rules = service.list_rules(
        campaign_id=campaign_id,
        team_id=team_id,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return rules


@router.get("/rules/{rule_id}", response_model=RoutingRuleResponse)
def get_routing_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific routing rule by ID."""
    service = RoutingService(db)

    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Routing rule {rule_id} not found"
        )

    return rule


@router.put("/rules/{rule_id}", response_model=RoutingRuleResponse)
def update_routing_rule(
    rule_id: int,
    rule_data: RoutingRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a routing rule."""
    service = RoutingService(db)

    rule = service.update_rule(rule_id, rule_data)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Routing rule {rule_id} not found"
        )

    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routing_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a routing rule."""
    service = RoutingService(db)

    success = service.delete_rule(rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Routing rule {rule_id} not found"
        )

    return None


# ===== Target Management =====

@router.post("/targets", response_model=RoutingTargetResponse, status_code=status.HTTP_201_CREATED)
def add_routing_target(
    target_data: RoutingTargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a target to a routing rule."""
    service = RoutingService(db)

    try:
        target = service.add_target(target_data)
        return target
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add routing target: {str(e)}"
        )


@router.get("/rules/{rule_id}/targets", response_model=list[RoutingTargetResponse])
def get_rule_targets(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all targets for a routing rule."""
    service = RoutingService(db)

    # Verify rule exists
    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Routing rule {rule_id} not found"
        )

    targets = service.get_rule_targets(rule_id)
    return targets


@router.delete("/targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_routing_target(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a target from a routing rule."""
    service = RoutingService(db)

    success = service.remove_target(target_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Routing target {target_id} not found"
        )

    return None


# ===== Call Routing =====

@router.post("/route", response_model=RouteCallResponse)
def route_call(
    request: RouteCallRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Route a call based on routing rules.

    Evaluates all applicable rules in priority order and selects the best target.
    """
    service = RoutingService(db)

    try:
        result = service.route_call(request)
        return RouteCallResponse(**result)
    except RoutingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to route call: {str(e)}"
        )


@router.post("/rules/{rule_id}/test", response_model=RouteCallResponse)
def test_routing_rule(
    rule_id: int,
    request: RouteCallRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test a routing rule with sample call data.

    Returns what the routing decision would be without actually routing the call.
    """
    service = RoutingService(db)

    # Verify rule exists
    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Routing rule {rule_id} not found"
        )

    try:
        # Run routing logic (this will create a log entry)
        result = service.route_call(request)
        return RouteCallResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test routing rule: {str(e)}"
        )


# ===== Analytics =====

@router.get("/analytics", response_model=dict)
def get_routing_analytics(
    rule_id: int | None = Query(None, description="Filter by specific rule"),
    start_date: datetime | None = Query(None, description="Start date for analytics range"),
    end_date: datetime | None = Query(None, description="End date for analytics range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get routing analytics."""
    service = RoutingService(db)

    analytics = service.get_routing_analytics(rule_id, start_date, end_date)
    return analytics


@router.get("/logs", response_model=list[RoutingLogResponse])
def get_routing_logs(
    rule_id: int | None = Query(None),
    call_sid: str | None = Query(None),
    success: bool | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get routing logs with optional filters."""
    from app.models.routing import RoutingLog

    query = db.query(RoutingLog)

    if rule_id:
        query = query.filter(RoutingLog.rule_id == rule_id)
    if call_sid:
        query = query.filter(RoutingLog.call_sid == call_sid)
    if success is not None:
        query = query.filter(RoutingLog.success == success)
    if start_date:
        query = query.filter(RoutingLog.route_start_time >= start_date)
    if end_date:
        query = query.filter(RoutingLog.route_start_time <= end_date)

    logs = query.order_by(RoutingLog.route_start_time.desc()).offset(skip).limit(limit).all()

    return logs


@router.get("/strategies", response_model=list[dict])
def get_available_strategies(
    current_user: User = Depends(get_current_user)
):
    """Get list of available routing strategies."""
    from app.models.routing import CallRoutingStrategy

    return [
        {"value": strategy.value, "name": strategy.name.replace("_", " ").title()}
        for strategy in CallRoutingStrategy
    ]
