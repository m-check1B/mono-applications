"""
Targeted tests to improve coverage for Settings Loader
"""
import pytest
import json
from unittest.mock import patch, mock_open
from pathlib import Path

from app.core.settings_loader import SettingsLoader

@pytest.fixture
def mock_settings_configs():
    """Mock models and prompts configuration JSONs"""
    models = {
        "providers": {
            "openai": {"models": {"gpt4": "openai/gpt-4"}},
            "anthropic": {"models": {"sonnet": "anthropic/claude-3-sonnet"}}
        },
        "useCases": {
            "chat": {
                "modelProvider": "openai",
                "modelKey": "gpt4",
                "fallback": "anthropic.sonnet"
            }
        }
    }
    prompts = {
        "templates": {
            "hello": {"template": "Hello {name}!", "variables": ["name"]}
        },
        "systemPrompts": {
            "base": {"role": "system", "content": "You are helpful."}
        },
        "escalationKeywords": ["urgent", "help"]
    }
    return models, prompts

def test_settings_loader_load_logic(mock_settings_configs):
    """Test loading configs from files"""
    models, prompts = mock_settings_configs
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=json.dumps(models))):
        
        # Reset singleton for test
        with (patch("app.core.settings_loader.MODELS_CONFIG", Path("/fake/models.json")), 
              patch("app.core.settings_loader.PROMPTS_CONFIG", Path("/fake/prompts.json"))):
            
            loader = SettingsLoader.__new__(SettingsLoader)
            # Manually trigger load with mock data
            with patch("json.load") as mock_json_load:
                mock_json_load.side_effect = [models, prompts]
                loader._load_configs()
                
                assert loader.get_model_for_use_case("chat") == "openai/gpt-4"
                assert loader.get_prompt_template("hello", name="World") == "Hello World!"
                assert loader.get_escalation_keywords() == ["urgent", "help"]
                assert loader.get_system_prompt("base") == {"role": "system", "content": "You are helpful."}

def test_get_model_fallback_logic(mock_settings_configs):
    """Test fallback when primary model is not found"""
    models, prompts = mock_settings_configs
    loader = SettingsLoader.__new__(SettingsLoader)
    loader._models_config = models
    loader._prompts_config = prompts
    
    # Test case where provider is missing
    loader._models_config["useCases"]["missing_provider"] = {
        "modelProvider": "nonexistent",
        "modelKey": "any",
        "fallback": "anthropic.sonnet"
    }
    
    model = loader.get_model_for_use_case("missing_provider")
    assert model == "anthropic/claude-3-sonnet"

def test_get_prompt_template_missing_variable(mock_settings_configs):
    """Test error when required variable is missing"""
    models, prompts = mock_settings_configs
    loader = SettingsLoader.__new__(SettingsLoader)
    loader._models_config = models
    loader._prompts_config = prompts
    
    with pytest.raises(ValueError, match="Missing required variable 'name'"):
        loader.get_prompt_template("hello") # Missing 'name'

def test_get_all_info(mock_settings_configs):
    """Test get_all_use_cases and get_all_providers"""
    models, prompts = mock_settings_configs
    loader = SettingsLoader.__new__(SettingsLoader)
    loader._models_config = models
    
    assert "chat" in loader.get_all_use_cases()
    assert "openai" in loader.get_all_providers()