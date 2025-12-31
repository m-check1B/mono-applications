"""
Speak by Kraliki - Alerts Router
View and manage automated alerts

RBAC enforced:
- owner, hr_director: View all alerts, configure alert rules
- manager: View alerts for their department, acknowledge alerts
"""

from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.rbac import (
    Permission,
    require_permission,
    can_view_all_departments,
    verify_department_access,
)
from app.models.alert import Alert
from app.models.department import Department
from app.schemas.alert import AlertResponse, AlertUpdate

router = APIRouter(prefix="/speak/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    severity: str | None = None,
    type_filter: str | None = None,
    is_read: bool | None = None,
    current_user: dict = Depends(require_permission(Permission.ALERTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List alerts for the company.

    RBAC: Managers only see alerts for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    query = (
        select(Alert)
        .where(Alert.company_id == company_id)
        .order_by(Alert.created_at.desc())
    )

    # Managers only see their department
    if user_role == "manager":
        dept_id = current_user.get("department_id")
        if dept_id:
            query = query.where(Alert.department_id == UUID(dept_id))

    if severity:
        query = query.where(Alert.severity == severity)
    if type_filter:
        query = query.where(Alert.type == type_filter)
    if is_read is not None:
        query = query.where(Alert.is_read == is_read)

    result = await db.execute(query)
    alerts = result.scalars().all()

    # Enrich with department names
    responses = []
    for alert in alerts:
        response = AlertResponse.model_validate(alert)
        if alert.department_id:
            dept_result = await db.execute(
                select(Department).where(Department.id == alert.department_id)
            )
            dept = dept_result.scalar_one_or_none()
            if dept:
                response.department_name = dept.name
        responses.append(response)

    return responses


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(require_permission(Permission.ALERTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread alerts.

    RBAC: Managers only see unread count for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    from sqlalchemy import func
    query = (
        select(func.count(Alert.id))
        .where(Alert.company_id == company_id)
        .where(Alert.is_read == False)
    )

    # Managers only see their department's alerts
    if not can_view_all_departments(user_role):
        dept_id = current_user.get("department_id")
        if dept_id:
            query = query.where(Alert.department_id == UUID(dept_id))
        else:
            # Manager without department sees count of 0
            return {"unread_count": 0}

    result = await db.execute(query)
    count = result.scalar()

    return {"unread_count": count or 0}


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    current_user: dict = Depends(require_permission(Permission.ALERTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get alert details.

    RBAC: Managers can only view alerts for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    result = await db.execute(
        select(Alert)
        .where(Alert.id == alert_id)
        .where(Alert.company_id == company_id)
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Managers can only view alerts for their department
    if not can_view_all_departments(user_role):
        if not verify_department_access(current_user, alert.department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this alert"
            )

    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    request: AlertUpdate,
    current_user: dict = Depends(require_permission(Permission.ALERTS_ACKNOWLEDGE)),
    db: AsyncSession = Depends(get_db)
):
    """Mark alert as read or resolved.

    RBAC: Managers can only update alerts for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    result = await db.execute(
        select(Alert)
        .where(Alert.id == alert_id)
        .where(Alert.company_id == company_id)
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Managers can only update alerts for their department
    if not can_view_all_departments(user_role):
        if not verify_department_access(current_user, alert.department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this alert"
            )

    if request.is_read is not None:
        alert.is_read = request.is_read
        if request.is_read and not alert.read_at:
            alert.read_at = datetime.utcnow()

    if request.is_resolved is not None:
        alert.is_resolved = request.is_resolved
        if request.is_resolved and not alert.resolved_at:
            alert.resolved_at = datetime.utcnow()

    await db.commit()
    await db.refresh(alert)

    return alert


@router.post("/{alert_id}/create-action")
async def create_action_from_alert(
    alert_id: UUID,
    current_user: dict = Depends(require_permission(Permission.ACTIONS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create action item from alert.

    RBAC: Managers can only create actions from alerts in their department.
    """
    from app.models.action import Action

    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    result = await db.execute(
        select(Alert)
        .where(Alert.id == alert_id)
        .where(Alert.company_id == company_id)
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    # Managers can only create actions from alerts in their department
    if not can_view_all_departments(user_role):
        if not verify_department_access(current_user, alert.department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this alert"
            )

    # Create action - inherit department from alert for RBAC
    action = Action(
        company_id=company_id,
        department_id=alert.department_id,  # Inherit department from alert
        topic=f"{alert.type.replace('_', ' ').title()} Alert",
        description=alert.description,
        created_from_alert_id=alert.id,
        priority="high" if alert.severity == "high" else "medium",
    )
    db.add(action)

    # Mark alert as having an action
    alert.is_read = True
    alert.read_at = datetime.utcnow()

    await db.commit()
    await db.refresh(action)

    return {
        "message": "Action created from alert",
        "action_id": str(action.id)
    }
