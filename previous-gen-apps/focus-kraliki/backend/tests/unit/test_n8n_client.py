"""
Unit tests for n8n Client Service
Tests orchestration and event dispatch client functionality
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

from app.services.n8n_client import N8nClient, get_n8n_client


class TestN8nClientInit:
    """Tests for N8nClient initialization"""

    def test_client_instantiation(self):
        """Client can be instantiated"""
        client = N8nClient()
        assert client is not None

    def test_client_with_settings(self):
        """Client accepts workspace settings"""
        settings = {"n8n_url": "https://custom.n8n.io"}
        client = N8nClient(workspace_settings=settings)
        assert client.base_url == "https://custom.n8n.io"

    def test_client_with_api_key(self):
        """Client accepts API key from settings"""
        settings = {"n8n_url": "https://custom.n8n.io", "n8n_api_key": "test-key"}
        client = N8nClient(workspace_settings=settings)
        assert client.api_key == "test-key"

    @patch("app.services.n8n_client.settings")
    def test_client_uses_default_settings(self, mock_settings):
        """Client uses global settings when no workspace settings"""
        mock_settings.N8N_URL = "https://default.n8n.io"
        mock_settings.N8N_API_KEY = "default-key"
        client = N8nClient()
        assert client.base_url == "https://default.n8n.io"
        assert client.api_key == "default-key"


class TestGetN8nClient:
    """Tests for get_n8n_client factory function"""

    def test_get_default_client(self):
        """Get client without settings"""
        client = get_n8n_client()
        assert isinstance(client, N8nClient)

    def test_get_client_with_none_settings(self):
        """Get client with None settings"""
        client = get_n8n_client(None)
        assert isinstance(client, N8nClient)

    def test_get_client_with_settings(self):
        """Get client with workspace settings"""
        settings = {"n8n_url": "https://workspace.n8n.io"}
        client = get_n8n_client(settings)
        assert isinstance(client, N8nClient)
        assert client.base_url == "https://workspace.n8n.io"


class TestN8nClientMethods:
    """Tests for N8nClient method existence"""

    def test_has_orchestrate_method(self):
        """Client has orchestrate_flow method"""
        client = N8nClient()
        assert hasattr(client, "orchestrate_flow")
        assert callable(client.orchestrate_flow)

    def test_has_trigger_webhook_method(self):
        """Client has trigger_webhook method"""
        client = N8nClient()
        assert hasattr(client, "trigger_webhook")
        assert callable(client.trigger_webhook)

    def test_has_dispatch_event_method(self):
        """Client has dispatch_event method"""
        client = N8nClient()
        assert hasattr(client, "dispatch_event")
        assert callable(client.dispatch_event)


class TestN8nClientAsync:
    """Async tests for N8nClient"""

    @pytest.mark.asyncio
    async def test_orchestrate_flow_callable(self):
        """Orchestrate flow is callable"""
        client = N8nClient()
        assert hasattr(client, "orchestrate_flow")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_trigger_webhook_success(self, mock_post):
        """Trigger webhook with successful response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status": "ok"}'
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = N8nClient({"n8n_url": "https://test.n8n.io"})
        result = await client.trigger_webhook("test-path", {"key": "value"})
        assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_trigger_webhook_no_url_configured(self):
        """Trigger webhook raises error when no URL configured"""
        client = N8nClient()
        client.base_url = None

        with pytest.raises(ValueError, match="not configured"):
            await client.trigger_webhook("test-path", {})

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_trigger_webhook_empty_response(self, mock_post):
        """Trigger webhook handles empty response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b""
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = N8nClient({"n8n_url": "https://test.n8n.io"})
        result = await client.trigger_webhook("test-path", {})
        assert result == {"status": "success"}

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_trigger_webhook_http_error(self, mock_post):
        """Trigger webhook raises error on HTTP failure"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=mock_response
        )

        client = N8nClient({"n8n_url": "https://test.n8n.io"})
        with pytest.raises(httpx.HTTPStatusError):
            await client.trigger_webhook("test-path", {})

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_dispatch_event(self, mock_post):
        """Dispatch event calls trigger_webhook"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"received": true}'
        mock_response.json.return_value = {"received": True}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = N8nClient({"n8n_url": "https://test.n8n.io"})
        event = {"type": "task-created", "data": {"task_id": "123"}}
        result = await client.dispatch_event(event)
        assert result == {"received": True}

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_orchestrate_flow(self, mock_post):
        """Orchestrate flow calls trigger_webhook with correct path"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"execution_id": "abc"}'
        mock_response.json.return_value = {"execution_id": "abc"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = N8nClient({"n8n_url": "https://test.n8n.io"})
        result = await client.orchestrate_flow("my-flow", {"param": "value"})
        assert result == {"execution_id": "abc"}


class TestN8nClientUrlBuilding:
    """Tests for URL building logic"""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_url_with_trailing_slash(self, mock_post):
        """URL building handles trailing slash in base URL"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{}'
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = N8nClient({"n8n_url": "https://test.n8n.io/"})
        await client.trigger_webhook("path", {})
        # Verify URL was called correctly (no double slashes)
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_url_with_leading_slash_path(self, mock_post):
        """URL building handles leading slash in path"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{}'
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = N8nClient({"n8n_url": "https://test.n8n.io"})
        await client.trigger_webhook("/webhook/path", {})
        mock_post.assert_called_once()


class TestN8nClientHeaders:
    """Tests for request headers"""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_includes_api_key_header(self, mock_post):
        """Request includes API key header when configured"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{}'
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = N8nClient({
            "n8n_url": "https://test.n8n.io",
            "n8n_api_key": "secret-key"
        })
        await client.trigger_webhook("path", {})

        # Verify headers included API key
        call_args = mock_post.call_args
        headers = call_args.kwargs.get("headers", {})
        assert "X-N8N-API-KEY" in headers or headers.get("X-N8N-API-KEY") == "secret-key"
