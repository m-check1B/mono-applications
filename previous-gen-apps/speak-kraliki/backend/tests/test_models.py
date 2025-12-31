"""
Speak by Kraliki - Model Tests
"""

import pytest
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.company import Company
from app.models.user import User
from app.models.employee import Employee
from app.models.department import Department
from app.models.survey import Survey
from app.models.conversation import Conversation
from app.models.alert import Alert
from app.models.action import Action


@pytest.mark.asyncio
async def test_company_creation(test_session: AsyncSession):
    """Test creating a company."""
    company = Company(
        name="New Test Company",
        slug="new-test-company",
        plan="growth",
    )
    test_session.add(company)
    await test_session.commit()

    result = await test_session.execute(
        select(Company).where(Company.slug == "new-test-company")
    )
    saved = result.scalar_one()
    assert saved.name == "New Test Company"
    assert saved.plan == "growth"
    assert saved.is_active is True


@pytest.mark.asyncio
async def test_user_company_relationship(test_session: AsyncSession, test_company: Company):
    """Test user-company relationship."""
    user = User(
        company_id=test_company.id,
        email="newuser@test.com",
        password_hash="hashed",
        first_name="New",
        last_name="User",
        role="manager",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    # Fetch with relationship
    result = await test_session.execute(
        select(User).where(User.email == "newuser@test.com")
    )
    saved_user = result.scalar_one()
    assert saved_user.company_id == test_company.id


@pytest.mark.asyncio
async def test_employee_department_relationship(
    test_session: AsyncSession,
    test_company: Company,
    test_department: Department
):
    """Test employee-department relationship."""
    employee = Employee(
        company_id=test_company.id,
        department_id=test_department.id,
        email="dept_emp@test.com",
        first_name="Department",
        last_name="Employee",
    )
    test_session.add(employee)
    await test_session.commit()
    await test_session.refresh(employee)

    result = await test_session.execute(
        select(Employee).where(Employee.email == "dept_emp@test.com")
    )
    saved_emp = result.scalar_one()
    assert saved_emp.department_id == test_department.id


@pytest.mark.asyncio
async def test_survey_questions_jsonb(test_session: AsyncSession, test_company: Company):
    """Test survey questions JSONB field."""
    questions = [
        {"id": 1, "question": "Question 1?", "follow_up_count": 1},
        {"id": 2, "question": "Question 2?", "follow_up_count": 2},
        {"id": 3, "question": "Question 3?", "follow_up_count": 0},
    ]

    survey = Survey(
        company_id=test_company.id,
        name="JSONB Test Survey",
        questions=questions,
    )
    test_session.add(survey)
    await test_session.commit()
    await test_session.refresh(survey)

    result = await test_session.execute(
        select(Survey).where(Survey.name == "JSONB Test Survey")
    )
    saved = result.scalar_one()
    assert len(saved.questions) == 3
    assert saved.questions[0]["question"] == "Question 1?"
    assert saved.questions[1]["follow_up_count"] == 2


@pytest.mark.asyncio
async def test_conversation_company_relationship(
    test_session: AsyncSession,
    test_company: Company,
    test_survey: Survey,
    test_employee: Employee
):
    """Test conversation has company_id."""
    conversation = Conversation(
        company_id=test_company.id,
        survey_id=test_survey.id,
        employee_id=test_employee.id,
        status="invited",
    )
    test_session.add(conversation)
    await test_session.commit()
    await test_session.refresh(conversation)

    result = await test_session.execute(
        select(Conversation).where(Conversation.id == conversation.id)
    )
    saved = result.scalar_one()
    assert saved.company_id == test_company.id


@pytest.mark.asyncio
async def test_conversation_transcript_jsonb(
    test_session: AsyncSession,
    test_conversation: Conversation
):
    """Test conversation transcript JSONB field."""
    transcript = [
        {"role": "ai", "content": "Hello!", "timestamp": "2024-01-01T10:00:00"},
        {"role": "user", "content": "Hi there", "timestamp": "2024-01-01T10:00:30"},
    ]

    test_conversation.transcript = transcript
    test_conversation.status = "completed"
    await test_session.commit()
    await test_session.refresh(test_conversation)

    result = await test_session.execute(
        select(Conversation).where(Conversation.id == test_conversation.id)
    )
    saved = result.scalar_one()
    assert len(saved.transcript) == 2
    assert saved.transcript[0]["role"] == "ai"


@pytest.mark.asyncio
async def test_conversation_sentiment_score(
    test_session: AsyncSession,
    test_conversation: Conversation
):
    """Test conversation sentiment score."""
    test_conversation.sentiment_score = Decimal("0.75")
    test_conversation.topics = ["workload", "management"]
    test_conversation.flags = ["positive_feedback"]
    await test_session.commit()
    await test_session.refresh(test_conversation)

    result = await test_session.execute(
        select(Conversation).where(Conversation.id == test_conversation.id)
    )
    saved = result.scalar_one()
    assert float(saved.sentiment_score) == 0.75
    assert "workload" in saved.topics


@pytest.mark.asyncio
async def test_alert_creation(
    test_session: AsyncSession,
    test_company: Company,
    test_conversation: Conversation
):
    """Test alert creation."""
    alert = Alert(
        company_id=test_company.id,
        conversation_id=test_conversation.id,
        type="flight_risk",
        severity="high",
        description="Employee showing signs of potential departure",
        trigger_keywords="leaving, new job, interview",  # Text field, not JSON
    )
    test_session.add(alert)
    await test_session.commit()
    await test_session.refresh(alert)

    result = await test_session.execute(
        select(Alert).where(Alert.id == alert.id)
    )
    saved = result.scalar_one()
    assert saved.type == "flight_risk"
    assert saved.severity == "high"
    assert saved.is_read is False


@pytest.mark.asyncio
async def test_action_creation(
    test_session: AsyncSession,
    test_company: Company,
    test_department: Department
):
    """Test action creation."""
    action = Action(
        company_id=test_company.id,
        topic="Workload concerns",
        status="new",
        notes="Multiple employees mentioned high workload",  # field is 'notes', not 'internal_notes'
    )
    test_session.add(action)
    await test_session.commit()
    await test_session.refresh(action)

    result = await test_session.execute(
        select(Action).where(Action.id == action.id)
    )
    saved = result.scalar_one()
    assert saved.topic == "Workload concerns"
    assert saved.status == "new"


@pytest.mark.asyncio
async def test_action_status_transition(
    test_session: AsyncSession,
    test_company: Company
):
    """Test action status transitions."""
    action = Action(
        company_id=test_company.id,
        topic="Test action",
        status="new",
    )
    test_session.add(action)
    await test_session.commit()

    # Transition to heard
    action.status = "heard"
    await test_session.commit()
    await test_session.refresh(action)
    assert action.status == "heard"

    # Transition to in_progress with message
    action.status = "in_progress"
    action.public_message = "We are addressing this concern"
    await test_session.commit()
    await test_session.refresh(action)
    assert action.status == "in_progress"
    assert action.public_message is not None

    # Transition to resolved
    action.status = "resolved"
    action.resolved_at = datetime.now(timezone.utc)
    await test_session.commit()
    await test_session.refresh(action)
    assert action.status == "resolved"
    assert action.resolved_at is not None


@pytest.mark.asyncio
async def test_employee_magic_link(
    test_session: AsyncSession,
    test_employee: Employee
):
    """Test employee magic link fields."""
    import secrets
    from datetime import timedelta

    token = secrets.token_urlsafe(32)
    test_employee.magic_link_token = token
    # Use naive datetime for SQLite compatibility (DateTime column without timezone)
    test_employee.magic_link_expires = datetime.utcnow() + timedelta(days=7)
    await test_session.commit()
    await test_session.refresh(test_employee)

    result = await test_session.execute(
        select(Employee).where(Employee.magic_link_token == token)
    )
    saved = result.scalar_one()
    assert saved.id == test_employee.id
    assert saved.magic_link_expires > datetime.utcnow()


@pytest.mark.asyncio
async def test_employee_vop_opt_out(
    test_session: AsyncSession,
    test_employee: Employee
):
    """Test employee Speak opt-out."""
    assert test_employee.vop_opted_out is False

    test_employee.vop_opted_out = True
    await test_session.commit()
    await test_session.refresh(test_employee)

    assert test_employee.vop_opted_out is True
