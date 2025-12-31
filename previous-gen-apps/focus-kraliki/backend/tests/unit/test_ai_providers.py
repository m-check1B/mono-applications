"""
Unit tests for AI Providers Service
Tests PromptLoader, AIProvider, and provider fallback logic
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.services.ai_providers import (
    PromptLoader,
    AIProvider,
    get_prompt,
    get_ai_provider,
)


class TestPromptLoader:
    """Tests for PromptLoader class"""

    def test_get_prompts_returns_dict(self):
        """get_prompts returns a dictionary"""
        prompts = PromptLoader.get_prompts()
        assert isinstance(prompts, dict)

    def test_get_prompts_has_categories(self):
        """Prompts contain expected categories"""
        prompts = PromptLoader.get_prompts()
        assert len(prompts) > 0

    def test_get_with_substitution(self):
        """get method substitutes variables"""
        result = PromptLoader.get("capture", "classify", input="test input")
        assert "test input" in result

    def test_get_missing_category_returns_empty(self):
        """get with missing category returns empty string"""
        result = PromptLoader.get("nonexistent", "key")
        assert result == ""

    def test_get_multiple_substitutions(self):
        """get substitutes multiple variables"""
        result = PromptLoader.get(
            "test_category", "test_key", var1="value1", var2="value2"
        )
        assert isinstance(result, str)


class TestAIProvider:
    """Tests for AIProvider class"""

    def test_init_default_settings(self):
        """Initialize with default settings from config"""
        provider = AIProvider()
        assert provider.model is not None
        assert provider.provider is not None

    def test_init_with_overrides(self):
        """Initialize with model and provider overrides"""
        provider = AIProvider(model="custom-model", provider="custom-provider")
        assert provider.model == "custom-model"
        assert provider.provider == "custom-provider"

    def test_init_has_fallback(self):
        """Provider has fallback model configured"""
        provider = AIProvider()
        assert provider.fallback_model is not None
        assert provider.fallback_provider is not None

    @pytest.mark.asyncio
    async def test_generate_uses_primary_provider(self):
        """generate uses primary provider"""
        provider = AIProvider(model="test-model", provider="gemini")

        with patch.object(
            provider, "_call_gemini", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = "test response"

            result = await provider.generate("test prompt")
            assert result == "test response"
            mock_call.assert_called_once_with("test-model", "test prompt", 1024)

    @pytest.mark.asyncio
    async def test_generate_with_custom_max_tokens(self):
        """generate respects custom max_tokens"""
        provider = AIProvider(model="test-model", provider="gemini")

        with patch.object(
            provider, "_call_gemini", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = "test response"

            await provider.generate("test prompt", max_tokens=2048)
            mock_call.assert_called_once_with("test-model", "test prompt", 2048)

    @pytest.mark.asyncio
    async def test_generate_uses_fallback_on_error(self):
        """generate uses fallback provider on error"""
        with patch("app.services.ai_providers.settings") as mock_settings:
            mock_settings.BRAIN_MODEL = "primary-model"
            mock_settings.BRAIN_MODEL_PROVIDER = "gemini"
            mock_settings.BRAIN_FALLBACK_MODEL = "fallback-model"
            mock_settings.BRAIN_FALLBACK_PROVIDER = "anthropic"

            provider = AIProvider()

            with patch.object(
                provider, "_call_gemini", new_callable=AsyncMock
            ) as mock_primary:
                mock_primary.side_effect = Exception("Primary failed")

            with patch.object(
                provider, "_call_anthropic", new_callable=AsyncMock
            ) as mock_fallback:
                mock_fallback.return_value = "fallback response"

                result = await provider.generate("test prompt")
                assert result == "fallback response"
                mock_fallback.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_raises_when_no_fallback(self):
        """generate raises exception when no fallback available"""
        with patch("app.services.ai_providers.settings") as mock_settings:
            mock_settings.BRAIN_MODEL = "primary-model"
            mock_settings.BRAIN_MODEL_PROVIDER = "gemini"
            mock_settings.BRAIN_FALLBACK_MODEL = None
            mock_settings.BRAIN_FALLBACK_PROVIDER = None

            provider = AIProvider()

            with patch.object(
                provider, "_call_gemini", new_callable=AsyncMock
            ) as mock_call:
                mock_call.side_effect = Exception("Primary failed")

                with pytest.raises(Exception):
                    await provider.generate("test prompt")

    @pytest.mark.asyncio
    async def test_call_gemini(self):
        """_call_gemini calls Google Gemini API"""
        provider = AIProvider(model="gemini-pro", provider="gemini")

        with patch("app.services.ai_providers.genai") as mock_genai:
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_response = Mock()
            mock_response.text = "gemini response"
            mock_model.generate_content.return_value = mock_response

            result = await provider._call_gemini("gemini-pro", "test prompt", 1024)
            assert result == "gemini response"
            mock_genai.configure.assert_called_once()
            mock_genai.GenerativeModel.assert_called_once_with("gemini-pro")
            mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_gemini_missing_api_key(self):
        """_call_gemini raises when API key missing"""
        provider = AIProvider(model="gemini-pro", provider="gemini")

        with patch("app.services.ai_providers.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = None

            with pytest.raises(ValueError, match="GEMINI_API_KEY not configured"):
                await provider._call_gemini("gemini-pro", "test prompt", 1024)

    @pytest.mark.asyncio
    async def test_call_anthropic(self):
        """_call_anthropic calls Anthropic Claude API"""
        provider = AIProvider(model="claude-3", provider="anthropic")

        with patch("app.services.ai_providers.Anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "claude response"
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response

            result = await provider._call_anthropic("claude-3", "test prompt", 1024)
            assert result == "claude response"
            mock_anthropic.assert_called_once()
            mock_client.messages.create.assert_called_once_with(
                model="claude-3",
                max_tokens=1024,
                messages=[{"role": "user", "content": "test prompt"}],
            )

    @pytest.mark.asyncio
    async def test_call_anthropic_missing_api_key(self):
        """_call_anthropic raises when API key missing"""
        provider = AIProvider(model="claude-3", provider="anthropic")

        with patch("app.services.ai_providers.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None

            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not configured"):
                await provider._call_anthropic("claude-3", "test prompt", 1024)

    @pytest.mark.asyncio
    async def test_call_glm(self):
        """_call_glm calls GLM API"""
        provider = AIProvider(model="glm-4", provider="glm")

        with patch("app.services.ai_providers.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "glm response"}}]
            }
            mock_client.post.return_value = mock_response

            result = await provider._call_glm("glm-4", "test prompt", 1024)
            assert result == "glm response"
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_glm_missing_api_key(self):
        """_call_glm raises when API key missing"""
        provider = AIProvider(model="glm-4", provider="glm")

        with patch("app.services.ai_providers.settings") as mock_settings:
            mock_settings.GLM_API_KEY = None

            with pytest.raises(ValueError, match="GLM_API_KEY not configured"):
                await provider._call_glm("glm-4", "test prompt", 1024)

    @pytest.mark.asyncio
    async def test_call_openrouter(self):
        """_call_openrouter calls OpenRouter API"""
        provider = AIProvider(model="custom-model", provider="openrouter")

        with patch("app.services.ai_providers.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "openrouter response"}}]
            }
            mock_client.post.return_value = mock_response

            result = await provider._call_openrouter(
                "custom-model", "test prompt", 1024
            )
            assert result == "openrouter response"
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_openrouter_missing_api_key(self):
        """_call_openrouter raises when API key missing"""
        provider = AIProvider(model="custom-model", provider="openrouter")

        with patch("app.services.ai_providers.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = None

            with pytest.raises(ValueError, match="OPENROUTER_API_KEY not configured"):
                await provider._call_openrouter("custom-model", "test prompt", 1024)

    @pytest.mark.asyncio
    async def test_call_unknown_provider_raises(self):
        """_call_provider raises for unknown provider"""
        provider = AIProvider(provider="unknown")

        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            await provider._call_provider("unknown", "model", "prompt", 1024)


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_get_prompt(self):
        """get_prompt is a convenient wrapper for PromptLoader.get"""
        result = get_prompt("capture", "classify", input="test")
        assert isinstance(result, str)

    def test_get_ai_provider(self):
        """get_ai_provider creates AIProvider instance"""
        provider = get_ai_provider(model="test-model", provider="test-provider")
        assert isinstance(provider, AIProvider)
        assert provider.model == "test-model"
        assert provider.provider == "test-provider"

    def test_get_ai_provider_defaults(self):
        """get_ai_provider uses defaults when no args"""
        provider = get_ai_provider()
        assert isinstance(provider, AIProvider)
        assert provider.model is not None


class TestAIProviderIntegration:
    """Integration tests for AI provider workflows"""

    @pytest.mark.asyncio
    async def test_full_generation_flow(self):
        """Test full generation flow with mock provider"""
        provider = AIProvider(model="test-model", provider="gemini")

        with patch.object(
            provider, "_call_gemini", new_callable=AsyncMock
        ) as mock_call:
            mock_call.return_value = "final response"

            result = await provider.generate("test prompt", max_tokens=500)
            assert result == "final response"
            mock_call.assert_called_once_with("test-model", "test prompt", 500)

    @pytest.mark.asyncio
    async def test_fallback_flow_integration(self):
        """Test fallback flow with multiple providers"""
        with patch("app.services.ai_providers.settings") as mock_settings:
            mock_settings.BRAIN_MODEL = "primary"
            mock_settings.BRAIN_MODEL_PROVIDER = "gemini"
            mock_settings.BRAIN_FALLBACK_MODEL = "fallback"
            mock_settings.BRAIN_FALLBACK_PROVIDER = "anthropic"

            provider = AIProvider()

            call_count = 0

            async def mock_primary(model, prompt, tokens):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("First call fails")
                return "primary success"

            async def mock_fallback(model, prompt, tokens):
                return "fallback success"

            with patch.object(
                provider,
                "_call_gemini",
                new_callable=AsyncMock,
                side_effect=mock_primary,
            ):
                with patch.object(
                    provider,
                    "_call_anthropic",
                    new_callable=AsyncMock,
                    side_effect=mock_fallback,
                ):
                    result = await provider.generate("test prompt")
                    assert result == "fallback success"
