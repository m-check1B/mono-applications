import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
from app.services.ai_providers import AIProvider, PromptLoader, get_prompt, get_ai_provider
from app.core.config import settings

@pytest.fixture
def mock_settings():
    with patch("app.services.ai_providers.settings") as mock:
        mock.BRAIN_MODEL = "test-model"
        mock.BRAIN_MODEL_PROVIDER = "gemini"
        mock.BRAIN_FALLBACK_MODEL = "fallback-model"
        mock.BRAIN_FALLBACK_PROVIDER = "anthropic"
        mock.GEMINI_API_KEY = "gemini-key"
        mock.ANTHROPIC_API_KEY = "anthropic-key"
        mock.GLM_API_KEY = "glm-key"
        mock.OPENROUTER_API_KEY = "openrouter-key"
        mock.BRAIN_PROMPTS_FILE = "config/brain_prompts.json"
        yield mock

class TestPromptLoader:
    @patch("app.services.ai_providers.Path.exists")
    def test_get_prompts_defaults(self, mock_exists):
        mock_exists.return_value = False
        PromptLoader._cache = None
        prompts = PromptLoader.get_prompts()
        assert "capture" in prompts
        assert prompts["capture"]["classify"] == "Classify: {input}"

    @patch("app.services.ai_providers.Path.exists")
    @patch("app.services.ai_providers.Path.stat")
    @patch("builtins.open", new_callable=pytest.importorskip("unittest.mock").mock_open, read_data='{"cat": {"key": "template {var}"}}')
    def test_get_prompts_file(self, mock_file, mock_stat, mock_exists):
        mock_exists.return_value = True
        mock_stat.return_value.st_mtime = 100
        PromptLoader._cache = None
        PromptLoader._cache_mtime = 0
        
        prompts = PromptLoader.get_prompts()
        assert prompts["cat"]["key"] == "template {var}"
        
        # Test substitution
        prompt = PromptLoader.get("cat", "key", var="val")
        assert prompt == "template val"

class TestAIProvider:
    @pytest.mark.asyncio
    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    async def test_call_gemini(self, mock_gen_model, mock_configure, mock_settings):
        provider = AIProvider(provider="gemini")
        mock_model_instance = mock_gen_model.return_value
        mock_response = MagicMock()
        mock_response.text = "Gemini Response"
        mock_model_instance.generate_content.return_value = mock_response
        
        response = await provider.generate("Hello")
        assert response == "Gemini Response"
        mock_configure.assert_called_with(api_key="gemini-key")

    @pytest.mark.asyncio
    @patch("app.services.ai_providers.Anthropic")
    async def test_call_anthropic(self, mock_anthropic, mock_settings):
        provider = AIProvider(provider="anthropic")
        mock_client = mock_anthropic.return_value
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Claude Response")]
        mock_client.messages.create.return_value = mock_message
        
        response = await provider.generate("Hello")
        assert response == "Claude Response"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_call_glm(self, mock_post, mock_settings):
        provider = AIProvider(provider="glm")
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "GLM Response"}}]}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        response = await provider.generate("Hello")
        assert response == "GLM Response"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_call_openrouter(self, mock_post, mock_settings):
        provider = AIProvider(provider="openrouter")
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "OpenRouter Response"}}]}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        response = await provider.generate("Hello")
        assert response == "OpenRouter Response"

    @pytest.mark.asyncio
    async def test_unknown_provider(self, mock_settings):
        mock_settings.BRAIN_FALLBACK_PROVIDER = None
        provider = AIProvider(provider="unknown")
        with pytest.raises(ValueError, match="Unknown provider: unknown"):
            await provider.generate("Hello")

    @pytest.mark.asyncio
    @patch.object(AIProvider, "_call_gemini", side_effect=Exception("Gemini failed"))
    @patch.object(AIProvider, "_call_anthropic", new_callable=AsyncMock)
    async def test_fallback_logic(self, mock_call_anthropic, mock_call_gemini, mock_settings):
        mock_call_anthropic.return_value = "Fallback Response"
        provider = AIProvider(provider="gemini") # Uses fallback to anthropic as per mock_settings
        
        response = await provider.generate("Hello")
        assert response == "Fallback Response"
        assert mock_call_gemini.called
        assert mock_call_anthropic.called

def test_convenience_functions(mock_settings):
    with patch.object(PromptLoader, "get", return_value="Prompt"):
        assert get_prompt("cat", "key") == "Prompt"
    
    provider = get_ai_provider()
    assert isinstance(provider, AIProvider)
