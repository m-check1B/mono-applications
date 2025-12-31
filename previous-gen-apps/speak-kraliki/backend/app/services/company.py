"""
Speak by Kraliki - Company Service
Multi-tenant isolation and access control (focus-lite pattern)
"""

from uuid import UUID
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.company import Company
from app.models.user import User


class CompanyService:
    """
    Service for company/tenant isolation.
    Pattern from focus-lite WorkspaceService.
    """

    @staticmethod
    async def get_company(
        company_id: UUID,
        db: AsyncSession
    ) -> Company:
        """Get company by ID or raise 404."""
        result = await db.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        return company

    @staticmethod
    async def require_company_access(
        user_payload: dict,
        company_id: UUID,
        db: AsyncSession
    ) -> Company:
        """
        Validate user has access to company.
        Raises 403 if user doesn't belong to this company.
        """
        user_company_id = UUID(user_payload["company_id"])

        if user_company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this company"
            )

        return await CompanyService.get_company(company_id, db)

    @staticmethod
    async def get_user_company(
        user_payload: dict,
        db: AsyncSession
    ) -> Company:
        """Get the company for the authenticated user."""
        company_id = UUID(user_payload["company_id"])
        return await CompanyService.get_company(company_id, db)

    @staticmethod
    def get_company_id(user_payload: dict) -> UUID:
        """Extract company_id from user token payload."""
        return UUID(user_payload["company_id"])

    @staticmethod
    def get_user_id(user_payload: dict) -> UUID:
        """Extract user_id from user token payload."""
        return UUID(user_payload["sub"])

    @staticmethod
    def get_user_role(user_payload: dict) -> str:
        """Extract role from user token payload."""
        return user_payload.get("role", "manager")

    @staticmethod
    def require_role(user_payload: dict, allowed_roles: list[str]) -> None:
        """
        Validate user has one of the allowed roles.
        Raises 403 if not.
        """
        role = CompanyService.get_user_role(user_payload)
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of: {', '.join(allowed_roles)}"
            )

    @staticmethod
    def require_owner_or_hr(user_payload: dict) -> None:
        """Require owner or HR director role."""
        CompanyService.require_role(user_payload, ["owner", "hr_director"])

    @staticmethod
    def require_owner(user_payload: dict) -> None:
        """Require owner role only."""
        CompanyService.require_role(user_payload, ["owner"])

    @staticmethod
    async def get_user_with_department_filter(
        user_payload: dict,
        db: AsyncSession
    ) -> tuple[UUID, Optional[UUID]]:
        """
        Get company_id and optional department_id filter.
        Managers can only see their department's data.
        Returns: (company_id, department_id or None for all)
        """
        company_id = CompanyService.get_company_id(user_payload)
        role = CompanyService.get_user_role(user_payload)

        # Owners and HR see all departments
        if role in ("owner", "hr_director"):
            return company_id, None

        # Managers see only their department
        user_id = CompanyService.get_user_id(user_payload)
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user and user.department_id:
            return company_id, user.department_id

        # No department assigned - see all (fallback)
        return company_id, None

    @staticmethod
    async def check_company_active(
        company_id: UUID,
        db: AsyncSession
    ) -> None:
        """
        Check if company subscription is active.
        Raises 403 if company is inactive.
        """
        company = await CompanyService.get_company(company_id, db)
        if not company.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company subscription is inactive"
            )

    @staticmethod
    async def check_plan_limit(
        company_id: UUID,
        feature: str,
        db: AsyncSession
    ) -> bool:
        """
        Check if company plan allows a feature.
        Returns True if allowed, raises 403 if not.
        """
        company = await CompanyService.get_company(company_id, db)

        # Plan limits (can be moved to config)
        plan_limits = {
            "starter": {
                "max_employees": 50,
                "max_surveys_per_month": 2,
                "ai_analysis": False,
                "custom_questions": False,
            },
            "growth": {
                "max_employees": 200,
                "max_surveys_per_month": 10,
                "ai_analysis": True,
                "custom_questions": True,
            },
            "scale": {
                "max_employees": 1000,
                "max_surveys_per_month": 999,
                "ai_analysis": True,
                "custom_questions": True,
            },
            "enterprise": {
                "max_employees": 999999,
                "max_surveys_per_month": 999,
                "ai_analysis": True,
                "custom_questions": True,
            },
        }

        limits = plan_limits.get(company.plan, plan_limits["starter"])

        if feature in limits:
            if isinstance(limits[feature], bool) and not limits[feature]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Feature '{feature}' not available on {company.plan} plan"
                )
            return True

        return True


# Convenience functions for dependency injection
async def get_company_service() -> CompanyService:
    """Dependency injection for CompanyService."""
    return CompanyService()
