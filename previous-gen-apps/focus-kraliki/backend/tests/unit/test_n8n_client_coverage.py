"""
N8n Client Unit Tests
Coverage target: 100% of n8n_client.py
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import httpx

from app.services.n8n_client import N8nClient, get_n8n_client


class TestN8nClientInit:
    """Test N8nClient initialization."""

    def test_init_default_settings(self):
        """Test init with default global settings."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = "global-key"

            client = N8nClient()

            assert client.base_url == "http://n8n.example.com"
            assert client.api_key == "global-key"

    def test_init_with_workspace_override(self):
        """Test init with workspace settings override."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://global.n8n.com"
            mock_settings.N8N_API_KEY = "global-key"

            workspace_settings = {
                "n8n_url": "http://custom.n8n.com",
                "n8n_api_key": "custom-key"
            }
            client = N8nClient(workspace_settings)

            assert client.base_url == "http://custom.n8n.com"
            assert client.api_key == "custom-key"

    def test_init_partial_workspace_override(self):
        """Test init with partial workspace override."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://global.n8n.com"
            mock_settings.N8N_API_KEY = "global-key"

            workspace_settings = {
                "n8n_url": "http://custom.n8n.com"
                # No api_key override
            }
            client = N8nClient(workspace_settings)

            assert client.base_url == "http://custom.n8n.com"
            assert client.api_key == "global-key"

    def test_init_no_url_logs_warning(self):
        """Test that missing URL logs warning."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = None
            mock_settings.N8N_API_KEY = None

            with patch("app.services.n8n_client.logger") as mock_logger:
                N8nClient()
                mock_logger.warning.assert_called()


class TestN8nClientTriggerWebhook:
    """Test trigger_webhook method."""

    @pytest.mark.asyncio
    async def test_trigger_webhook_no_url(self):
        """Test trigger fails when URL not configured."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = None
            mock_settings.N8N_API_KEY = None

            client = N8nClient()

            with pytest.raises(ValueError) as exc_info:
                await client.trigger_webhook("test", {"data": "value"})

            assert "not configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_trigger_webhook_success(self):
        """Test successful webhook trigger."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = "test-key"

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = MagicMock()
                mock_response.content = b'{"status": "ok"}'
                mock_response.json.return_value = {"status": "ok"}
                mock_response.raise_for_status = MagicMock()

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = N8nClient()
                result = await client.trigger_webhook("webhook-path", {"key": "value"})

                assert result == {"status": "ok"}
                mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_webhook_empty_response(self):
        """Test webhook with empty response."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = None

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = MagicMock()
                mock_response.content = b""  # Empty response
                mock_response.raise_for_status = MagicMock()

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = N8nClient()
                result = await client.trigger_webhook("test", {})

                assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_trigger_webhook_path_normalization(self):
        """Test path normalization with leading slash."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = None

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = MagicMock()
                mock_response.content = b'{}'
                mock_response.json.return_value = {}
                mock_response.raise_for_status = MagicMock()

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = N8nClient()
                await client.trigger_webhook("/webhook", {})

                call_args = mock_client.post.call_args
                url = call_args[0][0]
                assert url == "http://n8n.example.com/webhook"

    @pytest.mark.asyncio
    async def test_trigger_webhook_http_error(self):
        """Test HTTP error handling."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = "key"

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.text = "Internal error"

                http_error = httpx.HTTPStatusError(
                    "Server error",
                    request=MagicMock(),
                    response=mock_response
                )
                mock_response.raise_for_status.side_effect = http_error

                mock_client = AsyncMock()
                mock_client.post.return_value = mock_response
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = N8nClient()

                with pytest.raises(httpx.HTTPStatusError):
                    await client.trigger_webhook("test", {})

    @pytest.mark.asyncio
    async def test_trigger_webhook_generic_error(self):
        """Test generic error handling."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = None

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.post.side_effect = Exception("Connection error")
                mock_client.__aenter__.return_value = mock_client
                mock_client.__aexit__.return_value = None
                mock_client_class.return_value = mock_client

                client = N8nClient()

                with pytest.raises(Exception) as exc_info:
                    await client.trigger_webhook("test", {})

                assert "Connection error" in str(exc_info.value)


class TestN8nClientDispatchEvent:
    """Test dispatch_event method."""

    @pytest.mark.asyncio
    async def test_dispatch_event(self):
        """Test event dispatching."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = None

            with patch.object(N8nClient, "trigger_webhook") as mock_trigger:
                mock_trigger.return_value = {"dispatched": True}

                client = N8nClient()
                event = {"type": "task.created", "data": {}}
                result = await client.dispatch_event(event)

                mock_trigger.assert_called_once_with("events", event)
                assert result == {"dispatched": True}

    @pytest.mark.asyncio
    async def test_dispatch_event_custom_path(self):
        """Test event dispatching with custom path."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = None

            with patch.object(N8nClient, "trigger_webhook") as mock_trigger:
                mock_trigger.return_value = {}

                client = N8nClient()
                await client.dispatch_event({}, path="custom-events")

                mock_trigger.assert_called_once_with("custom-events", {})


class TestN8nClientOrchestrateFlow:
    """Test orchestrate_flow method."""

    @pytest.mark.asyncio
    async def test_orchestrate_flow(self):
        """Test flow orchestration."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = None

            with patch.object(N8nClient, "trigger_webhook") as mock_trigger:
                mock_trigger.return_value = {"flow_result": "success"}

                client = N8nClient()
                result = await client.orchestrate_flow(
                    "research-flow",
                    {"prospect_id": "123"}
                )

                expected_payload = {
                    "flow_id": "research-flow",
                    "context": {"prospect_id": "123"},
                    "source": "focus-kraliki-backend"
                }
                mock_trigger.assert_called_once_with("orchestrate/research-flow", expected_payload)
                assert result == {"flow_result": "success"}


class TestGetN8nClient:
    """Test get_n8n_client factory function."""

    def test_get_client_without_settings(self):
        """Test getting client without workspace settings."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = None

            client = get_n8n_client()
            assert isinstance(client, N8nClient)

    def test_get_client_with_settings(self):
        """Test getting client with workspace settings."""
        with patch("app.services.n8n_client.settings") as mock_settings:
            mock_settings.N8N_URL = "http://n8n.example.com"
            mock_settings.N8N_API_KEY = None

            settings = {"n8n_url": "http://custom.n8n.com"}
            client = get_n8n_client(settings)

            assert isinstance(client, N8nClient)
            assert client.base_url == "http://custom.n8n.com"
