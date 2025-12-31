"""
Speak by Kraliki - Test Configuration
Pytest fixtures for testing
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.auth import create_access_token, hash_password
from app.main import app
from app.middleware.rate_limit import limiter
from app.models.company import Company
from app.models.user import User
from app.models.employee import Employee
from app.models.department import Department
from app.models.survey import Survey
from app.models.conversation import Conversation
from app.models.alert import Alert
from app.models.action import Action


# Test database URL (SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Disable rate limiting for tests
limiter.enabled = False


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_company(test_session: AsyncSession) -> Company:
    """Create test company."""
    company = Company(
        id=uuid.uuid4(),
        name="Test Company",
        slug="test-company",
        plan="starter",
        is_active=True,
    )
    test_session.add(company)
    await test_session.commit()
    await test_session.refresh(company)
    return company


@pytest_asyncio.fixture
async def test_department(
    test_session: AsyncSession, test_company: Company
) -> Department:
    """Create test department."""
    department = Department(
        id=uuid.uuid4(),
        company_id=test_company.id,
        name="Engineering",
    )
    test_session.add(department)
    await test_session.commit()
    await test_session.refresh(department)
    return department


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession, test_company: Company) -> User:
    """Create test user."""
    user = User(
        id=uuid.uuid4(),
        company_id=test_company.id,
        email="admin@test.com",
        password_hash=hash_password("testpass123"),
        first_name="Test",
        last_name="Admin",
        role="owner",
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_employee(
    test_session: AsyncSession, test_company: Company, test_department: Department
) -> Employee:
    """Create test employee."""
    employee = Employee(
        id=uuid.uuid4(),
        company_id=test_company.id,
        department_id=test_department.id,
        email="employee@test.com",
        first_name="John",
        last_name="Doe",
        is_active=True,
        vop_opted_out=False,
    )
    test_session.add(employee)
    await test_session.commit()
    await test_session.refresh(employee)
    return employee


@pytest_asyncio.fixture
async def test_survey(test_session: AsyncSession, test_company: Company) -> Survey:
    """Create test survey."""
    survey = Survey(
        id=uuid.uuid4(),
        company_id=test_company.id,
        name="Monthly Check-in",
        description="Monthly employee check-in",
        status="draft",
        frequency="monthly",
        questions=[
            {"id": 1, "question": "How are you doing?", "follow_up_count": 1},
            {"id": 2, "question": "Any concerns?", "follow_up_count": 1},
        ],
    )
    test_session.add(survey)
    await test_session.commit()
    await test_session.refresh(survey)
    return survey


@pytest_asyncio.fixture
async def test_conversation(
    test_session: AsyncSession,
    test_company: Company,
    test_survey: Survey,
    test_employee: Employee,
) -> Conversation:
    """Create test conversation."""
    conversation = Conversation(
        id=uuid.uuid4(),
        company_id=test_company.id,
        survey_id=test_survey.id,
        employee_id=test_employee.id,
        status="invited",
        invited_at=datetime.now(timezone.utc),
        anonymous_id=f"EMP-{str(test_employee.id)[:8].upper()}",
    )
    test_session.add(conversation)
    await test_session.commit()
    await test_session.refresh(conversation)
    return conversation


@pytest.fixture
def auth_headers(test_user: User, test_company: Company) -> dict:
    """Create authentication headers."""
    token = create_access_token(
        data={
            "sub": str(test_user.id),
            "company_id": str(test_company.id),
            "role": test_user.role,
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_alert(
    test_session: AsyncSession,
    test_company: Company,
    test_conversation: Conversation,
    test_department: Department,
) -> Alert:
    """Create test alert."""
    alert = Alert(
        id=uuid.uuid4(),
        company_id=test_company.id,
        conversation_id=test_conversation.id,
        type="burnout",
        severity="high",
        department_id=test_department.id,
        description="Employee shows signs of burnout",
        trigger_keywords="exhausted, overwhelmed",
        is_read=False,
        is_resolved=False,
    )
    test_session.add(alert)
    await test_session.commit()
    await test_session.refresh(alert)
    return alert


@pytest_asyncio.fixture
async def test_action(
    test_session: AsyncSession, test_company: Company, test_department: Department
) -> Action:
    """Create test action."""
    action = Action(
        id=uuid.uuid4(),
        company_id=test_company.id,
        department_id=test_department.id,
        topic="Review workload policies",
        description="Review and potentially update workload policies to prevent burnout",
        status="new",
        priority="high",
        visible_to_employees=True,
        public_message="We're reviewing our workload policies based on your feedback.",
    )
    test_session.add(action)
    await test_session.commit()
    await test_session.refresh(action)
    return action
