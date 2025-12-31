"""
Speak by Kraliki - Survey Router
CRUD operations for surveys/campaigns

RBAC enforced:
- owner, hr_director: Full survey management
- manager: View surveys targeting their department only
"""

from uuid import UUID
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import get_current_user, generate_magic_link_token
from app.core.rbac import Permission, require_permission
from app.models.survey import Survey
from app.models.conversation import Conversation
from app.models.employee import Employee
from app.models.company import Company
from app.services.email import EmailService
from app.schemas.survey import (
    SurveyCreate,
    SurveyUpdate,
    SurveyResponse,
    SurveyStats,
)

router = APIRouter(prefix="/speak/surveys", tags=["surveys"])


@router.get("", response_model=list[SurveyResponse])
async def list_surveys(
    current_user: dict = Depends(require_permission(Permission.SURVEYS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List surveys for the company.

    RBAC: Managers only see surveys targeting their department.
    """
    company_id = UUID(current_user["company_id"])
    role = current_user.get("role")
    dept_id = current_user.get("department_id")

    query = select(Survey).where(Survey.company_id == company_id)

    # Scoping for managers
    if role == "manager" and dept_id:
        # PostgreSQL JSONB contains check: target_departments @> '["uuid"]'
        # Or check if it's null (all departments)
        query = query.where(
            or_(
                Survey.target_departments == None,
                Survey.target_departments.contains([str(dept_id)])
            )
        )

    result = await db.execute(query.order_by(Survey.created_at.desc()))
    surveys = result.scalars().all()

    # Add computed fields
    responses = []
    for survey in surveys:
        conv_result = await db.execute(
            select(func.count(Conversation.id))
            .where(Conversation.survey_id == survey.id)
        )
        total = conv_result.scalar()

        completed_result = await db.execute(
            select(func.count(Conversation.id))
            .where(Conversation.survey_id == survey.id)
            .where(Conversation.status == "completed")
        )
        completed = completed_result.scalar()

        response = SurveyResponse.model_validate(survey)
        response.conversation_count = total or 0
        response.completion_rate = (completed / total * 100) if total else 0
        responses.append(response)

    return responses


@router.post("", response_model=SurveyResponse)
async def create_survey(
    request: SurveyCreate,
    current_user: dict = Depends(require_permission(Permission.SURVEYS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create new survey.

    RBAC: Only owner and hr_director can create surveys.
    """
    company_id = UUID(current_user["company_id"])

    survey = Survey(
        company_id=company_id,
        name=request.name,
        description=request.description,
        frequency=request.frequency,
        questions=[q.model_dump() for q in request.questions],
        custom_system_prompt=request.custom_system_prompt,
        starts_at=request.starts_at,
        ends_at=request.ends_at,
        target_departments=[str(d) for d in request.target_departments] if request.target_departments else None,
    )
    db.add(survey)
    await db.commit()
    await db.refresh(survey)

    return survey


@router.get("/{survey_id}", response_model=SurveyResponse)
async def get_survey(
    survey_id: UUID,
    current_user: dict = Depends(require_permission(Permission.SURVEYS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get survey details."""
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .where(Survey.company_id == company_id)
    )
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    return survey


@router.patch("/{survey_id}", response_model=SurveyResponse)
async def update_survey(
    survey_id: UUID,
    request: SurveyUpdate,
    current_user: dict = Depends(require_permission(Permission.SURVEYS_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Update survey.

    RBAC: Only owner and hr_director can update surveys.
    """
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .where(Survey.company_id == company_id)
    )
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    if "questions" in update_data:
        update_data["questions"] = [q.model_dump() for q in request.questions]
    if "target_departments" in update_data and update_data["target_departments"]:
        update_data["target_departments"] = [str(d) for d in request.target_departments]

    for field, value in update_data.items():
        setattr(survey, field, value)

    survey.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(survey)

    return survey


@router.post("/{survey_id}/launch")
async def launch_survey(
    survey_id: UUID,
    current_user: dict = Depends(require_permission(Permission.SURVEYS_LAUNCH)),
    db: AsyncSession = Depends(get_db)
):
    """Launch survey and send invitations.

    RBAC: Only owner and hr_director can launch surveys.
    """
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .where(Survey.company_id == company_id)
    )
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    if survey.status not in ("draft", "paused"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey cannot be launched"
        )

    # Get company for email
    company_result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = company_result.scalar_one()

    # Get target employees
    query = select(Employee).where(
        Employee.company_id == company_id,
        Employee.is_active == True,
        Employee.vop_opted_out == False,
    )

    if survey.target_departments:
        dept_ids = [UUID(d) for d in survey.target_departments]
        query = query.where(Employee.department_id.in_(dept_ids))

    emp_result = await db.execute(query)
    employees = emp_result.scalars().all()

    # Create conversations and send invitations
    email_service = EmailService()
    invited_count = 0

    for employee in employees:
        # Generate magic link - returns (plaintext, hash)
        plaintext_token, hashed_token = generate_magic_link_token()
        employee.magic_link_token = hashed_token  # Store ONLY the hash
        employee.magic_link_expires = datetime.utcnow() + timedelta(days=7)

        # Create conversation
        conversation = Conversation(
            company_id=company_id,
            survey_id=survey.id,
            employee_id=employee.id,
            status="invited",
            invited_at=datetime.utcnow(),
            anonymous_id=f"EMP-{str(employee.id)[:8].upper()}",
        )
        db.add(conversation)

        # Send email with plaintext token
        base_url = settings.frontend_base_url.rstrip("/")
        magic_link = f"{base_url}/v/{plaintext_token}"
        await email_service.send_survey_invitation(
            to_email=employee.email,
            employee_name=employee.first_name,
            company_name=company.name,
            magic_link=magic_link,
            survey_name=survey.name,
        )
        invited_count += 1

    # Update survey status
    survey.status = "active"
    if not survey.starts_at:
        survey.starts_at = datetime.utcnow()

    await db.commit()

    return {
        "message": f"Survey launched, {invited_count} employees invited",
        "invited_count": invited_count,
    }


@router.post("/{survey_id}/pause")
async def pause_survey(
    survey_id: UUID,
    current_user: dict = Depends(require_permission(Permission.SURVEYS_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Pause active survey.

    RBAC: Only owner and hr_director can pause surveys.
    """
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .where(Survey.company_id == company_id)
    )
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    if survey.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey is not active"
        )

    survey.status = "paused"
    await db.commit()

    return {"message": "Survey paused"}


@router.get("/{survey_id}/stats", response_model=SurveyStats)
async def get_survey_stats(
    survey_id: UUID,
    current_user: dict = Depends(require_permission(Permission.SURVEYS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get survey statistics."""
    company_id = UUID(current_user["company_id"])

    # Verify survey belongs to company
    result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .where(Survey.company_id == company_id)
    )
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    # Get conversation stats
    conv_result = await db.execute(
        select(Conversation).where(Conversation.survey_id == survey_id)
    )
    conversations = conv_result.scalars().all()

    total = len(conversations)
    completed = sum(1 for c in conversations if c.status == "completed")
    in_progress = sum(1 for c in conversations if c.status == "in_progress")
    skipped = sum(1 for c in conversations if c.status == "skipped")

    durations = [c.duration_seconds for c in conversations if c.duration_seconds]
    sentiments = [float(c.sentiment_score) for c in conversations if c.sentiment_score]

    return SurveyStats(
        total_invited=total,
        total_completed=completed,
        total_in_progress=in_progress,
        total_skipped=skipped,
        completion_rate=(completed / total * 100) if total else 0,
        avg_duration_seconds=sum(durations) / len(durations) if durations else None,
        avg_sentiment=sum(sentiments) / len(sentiments) if sentiments else None,
    )
