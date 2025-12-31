"""
Settings and BYOK Integration Tests
Tests for settings endpoints and Bring Your Own Key functionality.
Target Coverage: 95%
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from unittest.mock import patch, AsyncMock

from app.models.user import User


class TestOpenRouterKeyManagement:
    """Test OpenRouter API key management (BYOK)."""

    @pytest.mark.asyncio
    async def test_save_openrouter_key(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test saving OpenRouter API key."""
        response = await async_client.post(
            "/settings/openrouter-key",
            json={"apiKey": "sk-or-v1-test-key-123"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "saved successfully" in data["message"]

        # Verify key saved in database
        db.refresh(test_user)
        assert test_user.openRouterApiKey == "sk-or-v1-test-key-123"

    @pytest.mark.asyncio
    async def test_save_openrouter_key_updates_existing(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test that saving a new key updates the existing one."""
        # Set initial key
        test_user.openRouterApiKey = "sk-or-v1-old-key"
        db.commit()

        # Update with new key
        response = await async_client.post(
            "/settings/openrouter-key",
            json={"apiKey": "sk-or-v1-new-key-456"},
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify key updated
        db.refresh(test_user)
        assert test_user.openRouterApiKey == "sk-or-v1-new-key-456"

    @pytest.mark.asyncio
    async def test_save_openrouter_key_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that saving API key requires authentication."""
        response = await async_client.post(
            "/settings/openrouter-key",
            json={"apiKey": "sk-or-v1-test-key"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_openrouter_key(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test deleting OpenRouter API key."""
        # Set key first
        test_user.openRouterApiKey = "sk-or-v1-test-key"
        db.commit()

        # Delete key
        response = await async_client.delete(
            "/settings/openrouter-key",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "removed" in data["message"]

        # Verify key removed from database
        db.refresh(test_user)
        assert test_user.openRouterApiKey is None

    @pytest.mark.asyncio
    async def test_delete_openrouter_key_when_none_exists(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test deleting key when none exists doesn't error."""
        # Ensure no key exists
        test_user.openRouterApiKey = None
        db.commit()

        # Delete (should succeed)
        response = await async_client.delete(
            "/settings/openrouter-key",
            headers=auth_headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_test_openrouter_key_valid(
        self,
        async_client: AsyncClient
    ):
        """Test validating a valid OpenRouter API key."""
        # Mock httpx response
        mock_response = AsyncMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            response = await async_client.post(
                "/settings/test-openrouter-key",
                json={"apiKey": "sk-or-v1-valid-key"}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "valid" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_test_openrouter_key_invalid(
        self,
        async_client: AsyncClient
    ):
        """Test validating an invalid OpenRouter API key."""
        # Mock httpx response (401 Unauthorized)
        mock_response = AsyncMock()
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            response = await async_client.post(
                "/settings/test-openrouter-key",
                json={"apiKey": "sk-or-v1-invalid-key"}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is False
            assert "failed" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_test_openrouter_key_network_error(
        self,
        async_client: AsyncClient
    ):
        """Test handling network errors when validating API key."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.side_effect = Exception("Network error")
            mock_client_class.return_value = mock_client

            response = await async_client.post(
                "/settings/test-openrouter-key",
                json={"apiKey": "sk-or-v1-test-key"}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is False
            assert "error" in data["message"].lower()


class TestUsageStats:
    """Test usage statistics endpoint."""

    @pytest.mark.asyncio
    async def test_get_usage_stats_free_tier(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test getting usage stats for free tier user."""
        # Setup free tier user
        test_user.isPremium = False
        test_user.openRouterApiKey = None
        test_user.usageCount = 25
        db.commit()

        response = await async_client.get(
            "/settings/usage-stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["usageCount"] == 25
        assert data["isPremium"] is False
        assert data["remainingUsage"] == 75  # 100 - 25
        assert data["hasCustomKey"] is False

    @pytest.mark.asyncio
    async def test_get_usage_stats_premium_user(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test getting usage stats for premium user."""
        # Setup premium user
        test_user.isPremium = True
        test_user.openRouterApiKey = None
        test_user.usageCount = 250
        db.commit()

        response = await async_client.get(
            "/settings/usage-stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["usageCount"] == 250
        assert data["isPremium"] is True
        assert data["remainingUsage"] is None  # No limit for premium
        assert data["hasCustomKey"] is False

    @pytest.mark.asyncio
    async def test_get_usage_stats_byok_user(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test getting usage stats for user with custom API key."""
        # Setup BYOK user
        test_user.isPremium = False
        test_user.openRouterApiKey = "sk-or-v1-custom-key"
        test_user.usageCount = 50
        db.commit()

        response = await async_client.get(
            "/settings/usage-stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["usageCount"] == 50
        assert data["isPremium"] is False
        assert data["remainingUsage"] is None  # No limit with BYOK
        assert data["hasCustomKey"] is True

    @pytest.mark.asyncio
    async def test_get_usage_stats_at_limit(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test getting usage stats when at free tier limit."""
        # Setup user at limit
        test_user.isPremium = False
        test_user.openRouterApiKey = None
        test_user.usageCount = 100
        db.commit()

        response = await async_client.get(
            "/settings/usage-stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["usageCount"] == 100
        assert data["remainingUsage"] == 0

    @pytest.mark.asyncio
    async def test_get_usage_stats_over_limit(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test getting usage stats when over limit (edge case)."""
        # Setup user over limit (shouldn't happen normally)
        test_user.isPremium = False
        test_user.openRouterApiKey = None
        test_user.usageCount = 105
        db.commit()

        response = await async_client.get(
            "/settings/usage-stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["usageCount"] == 105
        # Should be 0, not negative
        assert data["remainingUsage"] == 0

    @pytest.mark.asyncio
    async def test_get_usage_stats_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that usage stats endpoint requires authentication."""
        response = await async_client.get("/settings/usage-stats")

        assert response.status_code == 401


class TestBYOKIntegrationWithAI:
    """Test BYOK integration with AI endpoints."""

    @pytest.mark.asyncio
    async def test_byok_bypasses_usage_limit(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
        db: Session
    ):
        """Test that BYOK users bypass usage limits."""
        from unittest.mock import Mock

        # Setup user at free tier limit with custom key
        test_user_with_knowledge_types.isPremium = False
        test_user_with_knowledge_types.openRouterApiKey = "sk-or-v1-custom-key"
        test_user_with_knowledge_types.usageCount = 100
        db.commit()

        # Mock OpenRouter client
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_message.tool_calls = None
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_completion = Mock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create = Mock(return_value=mock_completion)

        with patch("app.routers.knowledge_ai.get_openrouter_client", return_value=mock_client):
            # Should succeed despite being at limit
            response = await async_client.post(
                "/knowledge-ai/chat",
                json={
                    "message": "Hello",
                    "conversationHistory": []
                },
                headers=auth_headers
            )

            assert response.status_code == 200

            # Usage count should NOT increment
            db.refresh(test_user_with_knowledge_types)
            assert test_user_with_knowledge_types.usageCount == 100

    @pytest.mark.asyncio
    async def test_byok_uses_custom_key(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
        db: Session
    ):
        """Test that BYOK users' custom key is used for API calls."""
        from unittest.mock import Mock

        custom_key = "sk-or-v1-user-custom-key"
        test_user_with_knowledge_types.openRouterApiKey = custom_key
        db.commit()

        # Mock OpenRouter to capture which key is used
        called_with_key = None

        def mock_get_client(api_key=None):
            nonlocal called_with_key
            called_with_key = api_key

            mock_client = Mock()
            mock_message = Mock()
            mock_message.content = "Response"
            mock_message.tool_calls = None
            mock_choice = Mock()
            mock_choice.message = mock_message
            mock_completion = Mock()
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create = Mock(return_value=mock_completion)
            return mock_client

        with patch("app.routers.knowledge_ai.get_openrouter_client", side_effect=mock_get_client):
            response = await async_client.post(
                "/knowledge-ai/chat",
                json={
                    "message": "Hello",
                    "conversationHistory": []
                },
                headers=auth_headers
            )

            assert response.status_code == 200

            # Verify custom key was used
            assert called_with_key == custom_key

    @pytest.mark.asyncio
    async def test_no_byok_uses_system_key(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
        db: Session
    ):
        """Test that users without BYOK use system key."""
        from unittest.mock import Mock

        test_user_with_knowledge_types.openRouterApiKey = None
        db.commit()

        # Mock OpenRouter to capture which key is used
        called_with_key = None

        def mock_get_client(api_key=None):
            nonlocal called_with_key
            called_with_key = api_key

            mock_client = Mock()
            mock_message = Mock()
            mock_message.content = "Response"
            mock_message.tool_calls = None
            mock_choice = Mock()
            mock_choice.message = mock_message
            mock_completion = Mock()
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create = Mock(return_value=mock_completion)
            return mock_client

        with patch("app.routers.knowledge_ai.get_openrouter_client", side_effect=mock_get_client):
            response = await async_client.post(
                "/knowledge-ai/chat",
                json={
                    "message": "Hello",
                    "conversationHistory": []
                },
                headers=auth_headers
            )

            assert response.status_code == 200

            # Verify system key was used (None passed to function)
            assert called_with_key is None


class TestSettingsEndpointSecurity:
    """Test security aspects of settings endpoints."""

    @pytest.mark.asyncio
    async def test_cannot_access_other_user_settings(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_2: User,
        db: Session
    ):
        """Test that users cannot access other users' settings."""
        # Set API key for user 2
        test_user_2.openRouterApiKey = "sk-or-v1-user2-key"
        db.commit()

        # User 1 tries to get their own stats
        response = await async_client.get(
            "/settings/usage-stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should not have user 2's key
        assert data["hasCustomKey"] is False

    @pytest.mark.asyncio
    async def test_api_key_not_exposed_in_responses(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test that API keys are never exposed in API responses."""
        # Set API key
        test_user.openRouterApiKey = "sk-or-v1-secret-key"
        db.commit()

        # Get usage stats
        response = await async_client.get(
            "/settings/usage-stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should only show boolean flag, not actual key
        assert data["hasCustomKey"] is True
        assert "openRouterApiKey" not in data
        assert "sk-or-v1-secret-key" not in str(data)
