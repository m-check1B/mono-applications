"""
Integration Test Fixtures
Shared fixtures for integration tests including auth, database, and mock services.
"""

import pytest
from typing import Generator, Dict, Any
from sqlalchemy.orm import Session
from unittest.mock import Mock, AsyncMock

from app.models.user import User
from app.models.item_type import ItemType
from app.core.security import generate_id
from app.services.knowledge_defaults import ensure_default_item_types


@pytest.fixture(scope="function")
def test_user_with_knowledge_types(db: Session, test_user: User) -> User:
    """
    Create test user with default knowledge types (Ideas, Notes, Tasks, Plans).

    Args:
        db: Database session
        test_user: Base test user

    Returns:
        User with default knowledge types
    """
    # Ensure default item types are created
    ensure_default_item_types(test_user.id, db)
    db.refresh(test_user)

    return test_user


@pytest.fixture(scope="function")
def knowledge_type_ids(db: Session, test_user_with_knowledge_types: User) -> Dict[str, str]:
    """
    Get IDs of default knowledge types for testing.

    Args:
        db: Database session
        test_user_with_knowledge_types: User with knowledge types

    Returns:
        Dictionary mapping type names to IDs
    """
    types = db.query(ItemType).filter(
        ItemType.userId == test_user_with_knowledge_types.id
    ).all()

    return {
        item_type.name: item_type.id
        for item_type in types
    }


@pytest.fixture(scope="function")
def agent_token(test_user: User) -> str:
    """
    Create valid agent token for II-Agent authentication.

    Args:
        test_user: Test user

    Returns:
        Agent JWT token
    """
    from app.core.security import create_agent_token
    return create_agent_token(data={"sub": test_user.id})


@pytest.fixture(scope="function")
def agent_headers(agent_token: str) -> dict:
    """
    Create authorization headers for agent requests.

    Args:
        agent_token: Agent JWT token

    Returns:
        Headers dictionary
    """
    return {"Authorization": f"Bearer {agent_token}"}


@pytest.fixture(scope="function")
def mock_openrouter():
    """
    Mock OpenRouter API client for testing AI functionality.

    Returns:
        Mock OpenRouter client
    """
    mock_client = Mock()
    mock_completion = Mock()
    mock_message = Mock()

    # Default response (no tool calls)
    mock_message.content = "I've created the task for you."
    mock_message.tool_calls = None

    mock_choice = Mock()
    mock_choice.message = mock_message

    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create = Mock(return_value=mock_completion)

    return mock_client


@pytest.fixture(scope="function")
def mock_openrouter_with_tools():
    """
    Mock OpenRouter API client that simulates tool calling.

    Returns:
        Mock OpenRouter client with tool calling
    """
    mock_client = Mock()

    # First response with tool calls
    mock_tool_call = Mock()
    mock_tool_call.id = "call_123"
    mock_tool_call.type = "function"
    mock_tool_call.function.name = "list_knowledge_item_types"
    mock_tool_call.function.arguments = "{}"

    first_message = Mock()
    first_message.content = None
    first_message.tool_calls = [mock_tool_call]

    first_choice = Mock()
    first_choice.message = first_message

    first_completion = Mock()
    first_completion.choices = [first_choice]

    # Second response after tool execution
    second_message = Mock()
    second_message.content = "I've listed your knowledge types."
    second_message.tool_calls = None

    second_choice = Mock()
    second_choice.message = second_message

    second_completion = Mock()
    second_completion.choices = [second_choice]

    # Return different responses on successive calls
    mock_client.chat.completions.create = Mock(
        side_effect=[first_completion, second_completion]
    )

    return mock_client


@pytest.fixture(scope="function")
async def mock_redis():
    """
    Mock Redis client for testing without real Redis.

    Returns:
        Mock Redis client
    """
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=None)
    mock_client.set = AsyncMock(return_value=True)
    mock_client.delete = AsyncMock(return_value=1)
    mock_client.close = AsyncMock()

    return mock_client
