"""
Speak by Kraliki - Conversations Router
Employee conversation management and transcript review

RBAC enforced:
- owner, hr_director: View all conversations across departments
- manager: View only conversations from their department's employees
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
)
from app.models.conversation import Conversation
from app.models.employee import Employee
from app.models.survey import Survey
from app.schemas.conversation import (
    ConversationResponse,
    ConversationEmployeeView,
    RedactRequest,
)

router = APIRouter(prefix="/speak", tags=["conversations"])


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    survey_id: UUID | None = None,
    status: str | None = None,
    current_user: dict = Depends(require_permission(Permission.CONVERSATIONS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List conversations for company.

    RBAC:
    - owner, hr_director: See all conversations
    - manager: Only see conversations from their department's employees
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role", "")

    # Build query through survey relationship
    query = (
        select(Conversation)
        .join(Survey)
        .where(Survey.company_id == company_id)
    )

    # Department scoping for managers
    if not can_view_all_departments(user_role):
        user_dept_id = current_user.get("department_id")
        if user_dept_id:
            # Join employee to filter by department
            query = query.join(Employee).where(Employee.department_id == UUID(user_dept_id))
        else:
            # Manager without department sees nothing
            query = query.where(False)

    if survey_id:
        query = query.where(Conversation.survey_id == survey_id)
    if status:
        query = query.where(Conversation.status == status)

    query = query.order_by(Conversation.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(require_permission(Permission.CONVERSATIONS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation details.

    RBAC: Managers can only view conversations from their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role", "")

    result = await db.execute(
        select(Conversation)
        .join(Survey)
        .where(Conversation.id == conversation_id)
        .where(Survey.company_id == company_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Department access check for managers
    if not can_view_all_departments(user_role):
        # Get the employee's department
        emp_result = await db.execute(
            select(Employee).where(Employee.id == conversation.employee_id)
        )
        employee = emp_result.scalar_one_or_none()

        user_dept_id = current_user.get("department_id")
        if employee and str(employee.department_id) != str(user_dept_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )

    return conversation


# Employee-facing endpoints (via magic link)

@router.get("/employee/transcript/{token}", response_model=ConversationEmployeeView)
async def get_employee_transcript(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Employee views their own transcript (Trust Layer v2.0).
    Accessed via magic link token.
    """
    # Hash the incoming token and look up by hash
    token_hash = hash_magic_link_token(token)
    emp_result = await db.execute(
        select(Employee).where(Employee.magic_link_token == token_hash)
    )
    employee = emp_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link"
        )

    if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )

    # Get most recent conversation
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.employee_id == employee.id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No conversation found"
        )

    return conversation


@router.post("/employee/transcript/{token}/redact")
async def redact_transcript(
    token: str,
    request: RedactRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Employee redacts parts of their transcript (Trust Layer v2.0).
    Removes specific turns from being analyzed.
    """
    # Hash the incoming token and look up by hash
    token_hash = hash_magic_link_token(token)
    emp_result = await db.execute(
        select(Employee).where(Employee.magic_link_token == token_hash)
    )
    employee = emp_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link"
        )

    if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )

    # Get most recent conversation
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.employee_id == employee.id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No conversation found"
        )

    if conversation.status not in ("completed", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot redact this conversation"
        )

    # Store redacted indices
    conversation.redacted_sections = request.turn_indices
    conversation.transcript_reviewed_by_employee = True

    # Mark redacted turns in transcript
    if conversation.transcript:
        for idx in request.turn_indices:
            if 0 <= idx < len(conversation.transcript):
                conversation.transcript[idx]["redacted"] = True
                conversation.transcript[idx]["content"] = "[REDACTED BY EMPLOYEE]"

    await db.commit()

    return {"message": "Transcript updated", "redacted_count": len(request.turn_indices)}


@router.post("/employee/consent/{token}")
async def record_consent(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Record explicit consent before conversation starts."""
    # Hash the incoming token and look up by hash
    token_hash = hash_magic_link_token(token)
    emp_result = await db.execute(
        select(Employee).where(Employee.magic_link_token == token_hash)
    )
    employee = emp_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link"
        )

    if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )

    # Log consent (in production, store this properly)
    return {
        "message": "Consent recorded",
        "employee_id": str(employee.id),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.delete("/employee/data/{token}")
async def delete_employee_data(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Employee requests deletion of their data (GDPR right to be forgotten).
    """
    # Hash the incoming token and look up by hash
    token_hash = hash_magic_link_token(token)
    emp_result = await db.execute(
        select(Employee).where(Employee.magic_link_token == token_hash)
    )
    employee = emp_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link"
        )

    if employee.magic_link_expires and employee.magic_link_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )

    # Delete all conversations
    conv_result = await db.execute(
        select(Conversation).where(Conversation.employee_id == employee.id)
    )
    conversations = conv_result.scalars().all()

    for conv in conversations:
        await db.delete(conv)

    # Clear Speak employee data (legacy vop fields)
    employee.vop_last_survey = None
    employee.vop_participation_rate = None
    employee.magic_link_token = None

    await db.commit()

    return {
        "message": "Your Speak by Kraliki data has been deleted",
        "deleted_conversations": len(conversations),
    }
