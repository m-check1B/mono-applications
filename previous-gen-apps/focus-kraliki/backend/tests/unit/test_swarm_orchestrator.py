import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.swarm_orchestrator import SwarmOrchestrator, get_swarm_orchestrator
from openai import AsyncOpenAI


@pytest.fixture
def mock_openai_client():
    client = MagicMock(spec=AsyncOpenAI)
    return client


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_n8n_client():
    return MagicMock()


class TestSwarmOrchestrator:
    def test_init(self, mock_db, mock_n8n_client):
        """Test SwarmOrchestrator initialization."""
        with patch(
            "app.services.swarm_orchestrator.get_n8n_client",
            return_value=mock_n8n_client,
        ):
            orchestrator = SwarmOrchestrator(mock_db)
            assert orchestrator.db == mock_db
            assert orchestrator.n8n == mock_n8n_client
            assert orchestrator._client is None

    @patch("app.services.swarm_orchestrator.get_n8n_client")
    def test_get_client_lazy_initialization(self, mock_get_n8n, mock_openai_client):
        """Test that OpenAI client is lazily initialized."""
        mock_n8n = MagicMock()
        mock_get_n8n.return_value = mock_n8n

        with patch.dict(
            "os.environ",
            {
                "AI_INTEGRATIONS_OPENROUTER_API_KEY": "test-key",
                "AI_INTEGRATIONS_OPENROUTER_BASE_URL": "https://test-url.com",
            },
        ):
            with patch(
                "app.services.swarm_orchestrator.OpenAI",
                return_value=mock_openai_client,
            ):
                orchestrator = SwarmOrchestrator()

                # First call creates client
                client1 = orchestrator.get_client()
                assert client1 == mock_openai_client
                assert orchestrator._client == mock_openai_client

                # Second call returns same instance
                client2 = orchestrator.get_client()
                assert client2 == client1
                assert orchestrator._client == mock_openai_client

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {
            "AI_INTEGRATIONS_OPENROUTER_API_KEY": "test-key",
            "AI_INTEGRATIONS_OPENROUTER_BASE_URL": "https://test-url.com",
        },
    )
    async def test_execute_swarm_success(self):
        """Test successful swarm execution."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = '{"summary": "Test plan", "steps": [{"agent": "TestAgent", "action": "Test action"}], "final_response": "Processing request"}'

        mock_chat_completions = MagicMock()
        mock_chat_completions.create.return_value = mock_response

        mock_client = MagicMock()
        mock_client.chat.completions = mock_chat_completions

        with patch("app.services.swarm_orchestrator.get_n8n_client"):
            with patch(
                "app.services.swarm_orchestrator.OpenAI", return_value=mock_client
            ):
                orchestrator = SwarmOrchestrator()

                result = await orchestrator.execute_swarm("Test message")

                assert result["summary"] == "Test plan"
                assert len(result["steps"]) == 1
                assert result["steps"][0]["agent"] == "TestAgent"
                assert result["steps"][0]["action"] == "Test action"
                assert result["final_response"] == "Processing request"

                mock_chat_completions.create.assert_called_once()
                call_args = mock_chat_completions.create.call_args
                assert call_args[1]["model"] == "openai/gpt-4o-mini"
                assert call_args[1]["response_format"] == {"type": "json_object"}

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {
            "AI_INTEGRATIONS_OPENROUTER_API_KEY": "test-key",
            "AI_INTEGRATIONS_OPENROUTER_BASE_URL": "https://test-url.com",
        },
    )
    async def test_execute_swarm_with_context(self):
        """Test swarm execution with context."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = '{"summary": "Test with context", "steps": [{"agent": "TestAgent", "action": "Action"}], "final_response": "Response"}'

        mock_chat_completions = MagicMock()
        mock_chat_completions.create.return_value = mock_response

        mock_client = MagicMock()
        mock_client.chat.completions = mock_chat_completions

        with patch("app.services.swarm_orchestrator.get_n8n_client"):
            with patch(
                "app.services.swarm_orchestrator.OpenAI", return_value=mock_client
            ):
                orchestrator = SwarmOrchestrator()

                context = {"user_id": "test-user", "workspace_id": "test-workspace"}
                result = await orchestrator.execute_swarm("Test message", context)

                assert result["summary"] == "Test with context"
                mock_chat_completions.create.assert_called_once()

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {
            "AI_INTEGRATIONS_OPENROUTER_API_KEY": "test-key",
            "AI_INTEGRATIONS_OPENROUTER_BASE_URL": "https://test-url.com",
        },
    )
    async def test_execute_swarm_api_error(self):
        """Test swarm execution handles API errors gracefully."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with patch("app.services.swarm_orchestrator.get_n8n_client"):
            with patch(
                "app.services.swarm_orchestrator.OpenAI", return_value=mock_client
            ):
                orchestrator = SwarmOrchestrator()

                result = await orchestrator.execute_swarm("Test message")

                assert result["summary"] == "Swarm fallback activated."
                assert len(result["steps"]) == 1
                assert result["steps"][0]["agent"] == "Director"
                assert result["steps"][0]["action"] == "Standard execution mode."
                assert "Test message" in result["final_response"]

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {
            "AI_INTEGRATIONS_OPENROUTER_API_KEY": "test-key",
            "AI_INTEGRATIONS_OPENROUTER_BASE_URL": "https://test-url.com",
        },
    )
    async def test_execute_swarm_invalid_json(self):
        """Test swarm execution handles invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON"

        mock_chat_completions = MagicMock()
        mock_chat_completions.create.return_value = mock_response

        mock_client = MagicMock()
        mock_client.chat.completions = mock_chat_completions

        with patch("app.services.swarm_orchestrator.get_n8n_client"):
            with patch(
                "app.services.swarm_orchestrator.OpenAI", return_value=mock_client
            ):
                orchestrator = SwarmOrchestrator()

                result = await orchestrator.execute_swarm("Test message")

                assert result["summary"] == "Swarm fallback activated."
                assert "Test message" in result["final_response"]

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {
            "AI_INTEGRATIONS_OPENROUTER_API_KEY": "test-key",
            "AI_INTEGRATIONS_OPENROUTER_BASE_URL": "https://test-url.com",
        },
    )
    async def test_execute_swarm_empty_message(self):
        """Test swarm execution with empty message."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = (
            '{"summary": "Empty", "steps": [], "final_response": "No message"}'
        )

        mock_chat_completions = MagicMock()
        mock_chat_completions.create.return_value = mock_response

        mock_client = MagicMock()
        mock_client.chat.completions = mock_chat_completions

        with patch("app.services.swarm_orchestrator.get_n8n_client"):
            with patch(
                "app.services.swarm_orchestrator.OpenAI", return_value=mock_client
            ):
                orchestrator = SwarmOrchestrator()

                result = await orchestrator.execute_swarm("")

                assert result["summary"] == "Empty"
                assert result["steps"] == []

    @patch("app.services.swarm_orchestrator.get_n8n_client")
    @patch("app.services.swarm_orchestrator.SwarmOrchestrator")
    def test_get_swarm_orchestrator(self, mock_swarm_class, mock_get_n8n):
        """Test get_swarm_orchestrator factory function."""
        mock_instance = MagicMock()
        mock_swarm_class.return_value = mock_instance

        result = get_swarm_orchestrator()

        mock_swarm_class.assert_called_once_with(None)
        assert result == mock_instance

    @patch("app.services.swarm_orchestrator.get_n8n_client")
    @patch("app.services.swarm_orchestrator.SwarmOrchestrator")
    def test_get_swarm_orchestrator_with_db(self, mock_swarm_class, mock_get_n8n):
        """Test get_swarm_orchestrator with database session."""
        mock_db = MagicMock()
        mock_instance = MagicMock()
        mock_swarm_class.return_value = mock_instance

        result = get_swarm_orchestrator(db=mock_db)

        mock_swarm_class.assert_called_once_with(mock_db)
        assert result == mock_instance
