"""
Speak by Kraliki - Role-Based Access Control (RBAC)

Provides permission-based authorization with department scoping.

Roles:
- owner: Full access, can manage billing, all departments
- hr_director: Full employee/survey access, all departments
- manager: Limited to their department, no billing access

Usage:
    from app.core.rbac import require_permission, Permission, department_scope

    @router.get("/employees")
    async def list_employees(
        current_user: dict = Depends(require_permission(Permission.EMPLOYEES_VIEW)),
        db: AsyncSession = Depends(get_db)
    ):
        # User is already verified to have permission
        # Apply department scoping if needed:
        query = department_scope(query, current_user, Employee)
        ...
"""

from enum import Enum
from functools import wraps
from typing import Callable, Optional, TypeVar, Type
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeBase

from app.core.auth import get_current_user


class Permission(str, Enum):
    """Granular permissions for RBAC."""

    # Employee management
    EMPLOYEES_VIEW = "employees:view"
    EMPLOYEES_CREATE = "employees:create"
    EMPLOYEES_UPDATE = "employees:update"
    EMPLOYEES_DELETE = "employees:delete"
    EMPLOYEES_IMPORT = "employees:import"

    # Department management
    DEPARTMENTS_VIEW = "departments:view"
    DEPARTMENTS_CREATE = "departments:create"
    DEPARTMENTS_UPDATE = "departments:update"
    DEPARTMENTS_DELETE = "departments:delete"

    # Survey management
    SURVEYS_VIEW = "surveys:view"
    SURVEYS_CREATE = "surveys:create"
    SURVEYS_UPDATE = "surveys:update"
    SURVEYS_DELETE = "surveys:delete"
    SURVEYS_LAUNCH = "surveys:launch"

    # Conversations/feedback
    CONVERSATIONS_VIEW = "conversations:view"
    CONVERSATIONS_VIEW_ALL = "conversations:view_all"  # Cross-department

    # Insights/Analytics
    INSIGHTS_VIEW = "insights:view"
    INSIGHTS_VIEW_ALL = "insights:view_all"  # Cross-department
    INSIGHTS_EXPORT = "insights:export"

    # Actions (follow-up tasks)
    ACTIONS_VIEW = "actions:view"
    ACTIONS_CREATE = "actions:create"
    ACTIONS_UPDATE = "actions:update"
    ACTIONS_DELETE = "actions:delete"

    # Alerts
    ALERTS_VIEW = "alerts:view"
    ALERTS_ACKNOWLEDGE = "alerts:acknowledge"
    ALERTS_CONFIGURE = "alerts:configure"

    # Billing/Admin
    BILLING_VIEW = "billing:view"
    BILLING_MANAGE = "billing:manage"
    USERS_VIEW = "users:view"
    USERS_MANAGE = "users:manage"
    SETTINGS_VIEW = "settings:view"
    SETTINGS_MANAGE = "settings:manage"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "owner": {
        # Owners can do everything
        Permission.EMPLOYEES_VIEW,
        Permission.EMPLOYEES_CREATE,
        Permission.EMPLOYEES_UPDATE,
        Permission.EMPLOYEES_DELETE,
        Permission.EMPLOYEES_IMPORT,
        Permission.DEPARTMENTS_VIEW,
        Permission.DEPARTMENTS_CREATE,
        Permission.DEPARTMENTS_UPDATE,
        Permission.DEPARTMENTS_DELETE,
        Permission.SURVEYS_VIEW,
        Permission.SURVEYS_CREATE,
        Permission.SURVEYS_UPDATE,
        Permission.SURVEYS_DELETE,
        Permission.SURVEYS_LAUNCH,
        Permission.CONVERSATIONS_VIEW,
        Permission.CONVERSATIONS_VIEW_ALL,
        Permission.INSIGHTS_VIEW,
        Permission.INSIGHTS_VIEW_ALL,
        Permission.INSIGHTS_EXPORT,
        Permission.ACTIONS_VIEW,
        Permission.ACTIONS_CREATE,
        Permission.ACTIONS_UPDATE,
        Permission.ACTIONS_DELETE,
        Permission.ALERTS_VIEW,
        Permission.ALERTS_ACKNOWLEDGE,
        Permission.ALERTS_CONFIGURE,
        Permission.BILLING_VIEW,
        Permission.BILLING_MANAGE,
        Permission.USERS_VIEW,
        Permission.USERS_MANAGE,
        Permission.SETTINGS_VIEW,
        Permission.SETTINGS_MANAGE,
    },

    "hr_director": {
        # HR can manage employees, surveys, view all departments
        Permission.EMPLOYEES_VIEW,
        Permission.EMPLOYEES_CREATE,
        Permission.EMPLOYEES_UPDATE,
        Permission.EMPLOYEES_DELETE,
        Permission.EMPLOYEES_IMPORT,
        Permission.DEPARTMENTS_VIEW,
        Permission.DEPARTMENTS_CREATE,
        Permission.DEPARTMENTS_UPDATE,
        Permission.SURVEYS_VIEW,
        Permission.SURVEYS_CREATE,
        Permission.SURVEYS_UPDATE,
        Permission.SURVEYS_DELETE,
        Permission.SURVEYS_LAUNCH,
        Permission.CONVERSATIONS_VIEW,
        Permission.CONVERSATIONS_VIEW_ALL,
        Permission.INSIGHTS_VIEW,
        Permission.INSIGHTS_VIEW_ALL,
        Permission.INSIGHTS_EXPORT,
        Permission.ACTIONS_VIEW,
        Permission.ACTIONS_CREATE,
        Permission.ACTIONS_UPDATE,
        Permission.ACTIONS_DELETE,
        Permission.ALERTS_VIEW,
        Permission.ALERTS_ACKNOWLEDGE,
        Permission.ALERTS_CONFIGURE,
        Permission.USERS_VIEW,
        Permission.SETTINGS_VIEW,
    },

    "manager": {
        # Managers have limited access, scoped to their department
        Permission.EMPLOYEES_VIEW,  # Only their department (enforced by scoping)
        Permission.DEPARTMENTS_VIEW,
        Permission.SURVEYS_VIEW,
        Permission.CONVERSATIONS_VIEW,  # Only their department
        Permission.INSIGHTS_VIEW,  # Only their department
        Permission.ACTIONS_VIEW,
        Permission.ACTIONS_CREATE,
        Permission.ACTIONS_UPDATE,
        Permission.ALERTS_VIEW,
        Permission.ALERTS_ACKNOWLEDGE,
    },
}


def get_user_permissions(role: str) -> set[Permission]:
    """Get all permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: str, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in get_user_permissions(role)


def can_view_all_departments(role: str) -> bool:
    """Check if role can view data across all departments."""
    return role in ("owner", "hr_director")


def require_permission(*permissions: Permission):
    """
    Dependency that checks if current user has required permission(s).
    All listed permissions must be present (AND logic).

    Usage:
        @router.get("/employees")
        async def list_employees(
            current_user: dict = Depends(require_permission(Permission.EMPLOYEES_VIEW))
        ):
            ...
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        user_role = current_user.get("role", "")
        user_permissions = get_user_permissions(user_role)

        missing = [p for p in permissions if p not in user_permissions]

        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission(s): {', '.join(p.value for p in missing)}"
            )

        return current_user

    return permission_checker


def require_any_permission(*permissions: Permission):
    """
    Dependency that checks if current user has ANY of the required permissions.
    At least one permission must be present (OR logic).
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        user_role = current_user.get("role", "")
        user_permissions = get_user_permissions(user_role)

        if not any(p in user_permissions for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(p.value for p in permissions)}"
            )

        return current_user

    return permission_checker


def department_scope(
    query: Select,
    current_user: dict,
    model: Type[DeclarativeBase],
    department_column: str = "department_id"
) -> Select:
    """
    Apply department scoping to a query based on user role.

    - Owners and HR Directors see all departments
    - Managers only see their own department

    Usage:
        query = select(Employee).where(Employee.company_id == company_id)
        query = department_scope(query, current_user, Employee)

    Args:
        query: SQLAlchemy select query
        current_user: Current user dict from auth
        model: SQLAlchemy model class
        department_column: Name of department_id column (default: "department_id")

    Returns:
        Modified query with department filter if applicable
    """
    user_role = current_user.get("role", "")

    # Owners and HR can see all departments
    if can_view_all_departments(user_role):
        return query

    # Managers only see their department
    user_dept_id = current_user.get("department_id")
    if user_dept_id:
        dept_column = getattr(model, department_column, None)
        if dept_column is not None:
            return query.where(dept_column == UUID(user_dept_id))

    # If manager has no department, they see nothing (safety default)
    # This prevents data leaks when department is not set
    dept_column = getattr(model, department_column, None)
    if dept_column is not None:
        return query.where(False)  # Return empty result

    return query


def verify_department_access(current_user: dict, department_id: UUID | str | None) -> bool:
    """
    Verify if user can access data for a specific department.

    Returns True if:
    - User is owner or hr_director (can access all)
    - User's department matches the requested department
    - department_id is None (not department-specific data)
    """
    if department_id is None:
        return True

    user_role = current_user.get("role", "")
    if can_view_all_departments(user_role):
        return True

    user_dept = current_user.get("department_id")
    if user_dept is None:
        return False

    return str(user_dept) == str(department_id)


def require_department_access(department_id_param: str = "department_id"):
    """
    Dependency that verifies user can access the specified department.

    Usage:
        @router.get("/employees")
        async def list_employees(
            department_id: UUID | None = None,
            current_user: dict = Depends(require_department_access("department_id"))
        ):
            ...
    """
    from fastapi import Query

    async def access_checker(
        request: Request,
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        # Get department_id from query params or path
        department_id = request.query_params.get(department_id_param)
        if not department_id:
            department_id = request.path_params.get(department_id_param)

        if department_id and not verify_department_access(current_user, department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this department"
            )

        return current_user

    return access_checker
