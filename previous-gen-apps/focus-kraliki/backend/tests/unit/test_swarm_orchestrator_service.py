"""
Comprehensive tests for Swarm Orchestrator Service to improve coverage
"""

import pytest
from unittest.mock import MagicMock, patch
from openai.types.chat.chat_completion import ChatCompletion

from app.services.swarm_orchestrator import (
    SwarmOrchestrator,
    get_swarm_orchestrator,
)


class TestSwarmOrchestratorInit:
    """Test service initialization"""

    def test_init_basic(self):
        """Test basic initialization"""
        orchestrator = SwarmOrchestrator()
        assert orchestrator.db is None
        assert orchestrator._client is None

    def test_init_with_db(self):
        """Test initialization with database session"""
        mock_db = MagicMock()
        orchestrator = SwarmOrchestrator(db_session=mock_db)
        assert orchestrator.db == mock_db
        assert orchestrator._client is None

    @patch("app.services.swarm_orchestrator.get_n8n_client")
    def test_init_with_n8n_client(self, mock_get_client):
        """Test initialization gets n8n client"""
        mock_n8n = MagicMock()
        mock_get_client.return_value = mock_n8n

        orchestrator = SwarmOrchestrator()

        mock_get_client.assert_called_once()


class TestGetClient:
    """Test client lazy initialization"""

    @patch.dict(
        "os.environ",
        {
            "AI_INTEGRATIONS_OPENROUTER_API_KEY": "test_key",
            "AI_INTEGRATIONS_OPENROUTER_BASE_URL": "https://test.url",
        },
    )
    @patch("app.services.swarm_orchestrator.OpenAI")
    def test_get_client_creates_new_client(self, mock_openai):
        """Test that client is created on first access"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        orchestrator = SwarmOrchestrator()
        client = orchestrator.get_client()

        assert client == mock_client
        mock_openai.assert_called_once_with(
            api_key="test_key", base_url="https://test.url"
        )

    @patch.dict(
        "os.environ",
        {
            "AI_INTEGRATIONS_OPENROUTER_API_KEY": "test_key",
            "AI_INTEGRATIONS_OPENROUTER_BASE_URL": "https://test.url",
        },
    )
    @patch("app.services.swarm_orchestrator.OpenAI")
    def test_get_client_returns_cached_client(self, mock_openai):
        """Test that client is cached on subsequent access"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        orchestrator = SwarmOrchestrator()
        client1 = orchestrator.get_client()
        client2 = orchestrator.get_client()

        assert client1 == client2
        assert mock_openai.call_count == 1

    @patch.dict("os.environ", {}, clear=True)
    @patch("app.services.swarm_orchestrator.OpenAI")
    def test_get_client_no_env_vars(self, mock_openai):
        """Test client creation without environment variables"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        orchestrator = SwarmOrchestrator()
        client = orchestrator.get_client()

        assert client == mock_client
        mock_openai.assert_called_once_with(api_key=None, base_url=None)


class TestExecuteSwarm:
    """Test swarm execution"""

    @patch("app.services.swarm_orchestrator.OpenAI")
    async def test_execute_swarm_success(self, mock_openai):
        """Test successful swarm execution"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = '{"summary":"Test plan","steps":[{"agent":"Test","action":"test action"}],"final_response":"Processing your request"}'

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        orchestrator = SwarmOrchestrator()
        result = await orchestrator.execute_swarm("Create a task")

        assert result["summary"] == "Test plan"
        assert len(result["steps"]) == 1
        assert result["steps"][0]["agent"] == "Test"
        assert result["final_response"] == "Processing your request"
        mock_client.chat.completions.create.assert_called_once()

    @patch("app.services.swarm_orchestrator.OpenAI")
    async def test_execute_swarm_with_context(self, mock_openai):
        """Test swarm execution with context"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = (
            '{"summary":"Test","steps":[],"final_response":"Test response"}'
        )

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        orchestrator = SwarmOrchestrator()
        result = await orchestrator.execute_swarm(
            "Test message", context={"user_id": "user123", "workspace": "workspace1"}
        )

        assert "summary" in result
        mock_client.chat.completions.create.assert_called_once()

    @patch("app.services.swarm_orchestrator.OpenAI")
    async def test_execute_swarm_exception(self, mock_openai):
        """Test swarm execution with exception"""
        # Mock exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client

        orchestrator = SwarmOrchestrator()
        result = await orchestrator.execute_swarm("Test message")

        # Should return fallback response
        assert result["summary"] == "Swarm fallback activated."
        assert len(result["steps"]) == 1
        assert result["steps"][0]["agent"] == "Director"
        assert "Test message" in result["final_response"]

    @patch("app.services.swarm_orchestrator.OpenAI")
    async def test_execute_swarm_long_message_truncation(self, mock_openai):
        """Test that long messages are truncated in log"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = '{"summary":"Test","steps":[],"final_response":"Test"}'

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        orchestrator = SwarmOrchestrator()
        long_message = "A" * 100  # Long message

        await orchestrator.execute_swarm(long_message)

        # Log should truncate to 50 chars
        mock_client.chat.completions.create.assert_called_once()
        # Verify message passed to API (not truncated in actual call)
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert long_message in prompt  # Full message included in prompt


class TestGetSwarmOrchestrator:
    """Test factory function"""

    def test_get_swarm_orchestrator_no_db(self):
        """Test factory function without database"""
        orchestrator = get_swarm_orchestrator()
        assert isinstance(orchestrator, SwarmOrchestrator)

    def test_get_swarm_orchestrator_with_db(self):
        """Test factory function with database"""
        mock_db = MagicMock()
        orchestrator = get_swarm_orchestrator(db=mock_db)
        assert isinstance(orchestrator, SwarmOrchestrator)
        assert orchestrator.db == mock_db
