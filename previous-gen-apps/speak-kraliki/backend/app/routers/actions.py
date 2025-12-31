"""
Speak by Kraliki - Actions Router
Action Loop v2.0: Track leadership responses to feedback

RBAC enforced:
- owner, hr_director, manager: View and manage actions
- manager: Limited to actions in their department scope
"""

from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import get_current_user, hash_magic_link_token
from app.core.rbac import (
    Permission,
    require_permission,
    can_view_all_departments,
    verify_department_access,
)
from app.models.action import Action
from app.models.user import User
from app.schemas.action import (
    ActionCreate,
    ActionUpdate,
    ActionResponse,
    ActionPublic,
)

router = APIRouter(prefix="/speak/actions", tags=["actions"])


@router.get("", response_model=list[ActionResponse])
async def list_actions(
    status_filter: str | None = None,
    current_user: dict = Depends(require_permission(Permission.ACTIONS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List all actions for the company.

    RBAC: Managers only see actions for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    query = (
        select(Action)
        .where(Action.company_id == company_id)
        .order_by(Action.created_at.desc())
    )

    # Managers only see their department's actions
    if not can_view_all_departments(user_role):
        dept_id = current_user.get("department_id")
        if dept_id:
            query = query.where(Action.department_id == UUID(dept_id))
        else:
            # Manager without department sees nothing
            query = query.where(False)

    if status_filter:
        query = query.where(Action.status == status_filter)

    result = await db.execute(query)
    actions = result.scalars().all()

    # Enrich with assigned user name
    responses = []
    for action in actions:
        response = ActionResponse.model_validate(action)
        if action.assigned_to:
            user_result = await db.execute(
                select(User).where(User.id == action.assigned_to)
            )
            user = user_result.scalar_one_or_none()
            if user:
                response.assigned_to_name = user.full_name
        responses.append(response)

    return responses


@router.post("", response_model=ActionResponse)
async def create_action(
    request: ActionCreate,
    current_user: dict = Depends(require_permission(Permission.ACTIONS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create new action (from alert or manually).

    RBAC: If department_id is provided, managers can only create actions for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    # Determine department_id
    department_id = None
    if hasattr(request, 'department_id') and request.department_id:
        department_id = request.department_id
        # Managers can only create actions for their department
        if not can_view_all_departments(user_role):
            if not verify_department_access(current_user, department_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this department"
                )

    action = Action(
        company_id=company_id,
        department_id=department_id,
        topic=request.topic,
        description=request.description,
        created_from_alert_id=request.created_from_alert_id,
        assigned_to=request.assigned_to,
        priority=request.priority,
        visible_to_employees=request.visible_to_employees,
        public_message=request.public_message,
    )
    db.add(action)
    await db.commit()
    await db.refresh(action)

    return action


@router.get("/public", response_model=list[ActionPublic])
async def list_public_actions(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    List actions visible to employees (Action Loop widget).
    Accessed via magic link token.
    """
    from app.models.employee import Employee

    # Hash the incoming token and look up by hash
    token_hash = hash_magic_link_token(token)
    emp_result = await db.execute(
        select(Employee).where(Employee.magic_link_token == token_hash)
    )
    employee = emp_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid link"
        )

    if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )

    # Get visible actions
    result = await db.execute(
        select(Action)
        .where(Action.company_id == employee.company_id)
        .where(Action.visible_to_employees == True)
        .order_by(Action.updated_at.desc())
        .limit(10)
    )
    actions = result.scalars().all()

    return actions


@router.get("/{action_id}", response_model=ActionResponse)
async def get_action(
    action_id: UUID,
    current_user: dict = Depends(require_permission(Permission.ACTIONS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get action details.

    RBAC: Managers can only view actions for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    result = await db.execute(
        select(Action)
        .where(Action.id == action_id)
        .where(Action.company_id == company_id)
    )
    action = result.scalar_one_or_none()

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )

    # Managers can only view actions for their department
    if not can_view_all_departments(user_role):
        if not verify_department_access(current_user, action.department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this action"
            )

    return action


@router.patch("/{action_id}", response_model=ActionResponse)
async def update_action(
    action_id: UUID,
    request: ActionUpdate,
    current_user: dict = Depends(require_permission(Permission.ACTIONS_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Update action status or details.

    RBAC: Managers can only update actions for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role")

    result = await db.execute(
        select(Action)
        .where(Action.id == action_id)
        .where(Action.company_id == company_id)
    )
    action = result.scalar_one_or_none()

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )

    # Managers can only update actions for their department
    if not can_view_all_departments(user_role):
        if not verify_department_access(current_user, action.department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this action"
            )

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(action, field, value)

    # Set resolved_at timestamp if status changed to resolved
    if request.status == "resolved" and not action.resolved_at:
        action.resolved_at = datetime.utcnow()

    action.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(action)

    return action


@router.delete("/{action_id}")
async def delete_action(
    action_id: UUID,
    current_user: dict = Depends(require_permission(Permission.ACTIONS_DELETE)),
    db: AsyncSession = Depends(get_db)
):
    """Delete action.

    RBAC: Only owner and hr_director can delete actions.
    """
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Action)
        .where(Action.id == action_id)
        .where(Action.company_id == company_id)
    )
    action = result.scalar_one_or_none()

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )

    await db.delete(action)
    await db.commit()

    return {"message": "Action deleted"}
