"""
Settings Loader - Centralized configuration management

This module provides a clean interface to load AI models and prompts from JSON config files
instead of hardcoding them throughout the application.

Usage:
    from app.core.settings_loader import get_model_for_use_case, get_prompt_template

    # Get model for a specific use case
    model = get_model_for_use_case("chat")  # Returns "anthropic/claude-3.5-sonnet:beta"

    # Get prompt template
    prompt = get_prompt_template("parseTask", input="Buy groceries")
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Path to settings directory
SETTINGS_DIR = Path(__file__).parent.parent.parent.parent / "settings"
MODELS_CONFIG = SETTINGS_DIR / "models" / "ai_models.json"
PROMPTS_CONFIG = SETTINGS_DIR / "prompts" / "ai_prompts.json"


class SettingsLoader:
    """Singleton settings loader for AI models and prompts"""

    _instance = None
    _models_config: Optional[Dict[str, Any]] = None
    _prompts_config: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_configs()
        return cls._instance

    def _load_configs(self):
        """Load configuration files"""
        try:
            # Load models config
            if MODELS_CONFIG.exists():
                with open(MODELS_CONFIG, "r") as f:
                    self._models_config = json.load(f)
                logger.info(f"Loaded models config from {MODELS_CONFIG}")
            else:
                logger.warning(f"Models config not found at {MODELS_CONFIG}")
                self._models_config = {}

            # Load prompts config
            if PROMPTS_CONFIG.exists():
                with open(PROMPTS_CONFIG, "r") as f:
                    self._prompts_config = json.load(f)
                logger.info(f"Loaded prompts config from {PROMPTS_CONFIG}")
            else:
                logger.warning(f"Prompts config not found at {PROMPTS_CONFIG}")
                self._prompts_config = {}

        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self._models_config = {}
            self._prompts_config = {}

    def reload(self):
        """Reload configuration files (useful for development)"""
        self._load_configs()

    def get_model_for_use_case(self, use_case: str, use_fallback: bool = True) -> str:
        """
        Get model name for a specific use case

        Args:
            use_case: The use case (e.g., "chat", "parseTask", "orchestrateTask")
            use_fallback: Whether to use fallback model if primary fails

        Returns:
            Model identifier string (e.g., "anthropic/claude-3.5-sonnet:beta")

        Raises:
            ValueError: If use case not found and no fallback available
        """
        if not self._models_config:
            raise ValueError("Models configuration not loaded")

        # Get use case config
        use_cases = self._models_config.get("useCases", {})
        if use_case not in use_cases:
            raise ValueError(f"Use case '{use_case}' not found in configuration")

        config = use_cases[use_case]
        provider = config.get("modelProvider")
        model_key = config.get("modelKey")

        # Get model from provider
        try:
            providers = self._models_config.get("providers", {})
            if provider not in providers:
                raise ValueError(f"Provider '{provider}' not found")

            provider_config = providers[provider]
            models = provider_config.get("models", {})

            if model_key not in models:
                raise ValueError(
                    f"Model key '{model_key}' not found in provider '{provider}'"
                )

            return models[model_key]

        except Exception as e:
            logger.error(f"Error getting model for use case '{use_case}': {e}")

            # Try fallback
            if use_fallback and "fallback" in config:
                fallback = config["fallback"]
                logger.info(f"Using fallback model: {fallback}")

                # Parse fallback (format: "provider.modelKey")
                if "." in fallback:
                    fb_provider, fb_key = fallback.split(".", 1)
                    try:
                        return providers[fb_provider]["models"][fb_key]
                    except Exception as e:
                        logger.debug(f"Fallback model '{fallback}' not found: {e}")

            # Last resort: return a default
            logger.warning(f"Falling back to hardcoded default for '{use_case}'")
            return "anthropic/claude-3.5-sonnet:beta"

    def get_model_config(self, use_case: str) -> Dict[str, Any]:
        """
        Get full model configuration for a use case including parameters

        Args:
            use_case: The use case (e.g., "chat", "orchestrateTask")

        Returns:
            Dictionary with model, maxTokens, temperature, etc.
        """
        if not self._models_config:
            raise ValueError("Models configuration not loaded")

        use_cases = self._models_config.get("useCases", {})
        if use_case not in use_cases:
            raise ValueError(f"Use case '{use_case}' not found")

        config = use_cases[use_case].copy()
        config["model"] = self.get_model_for_use_case(use_case)

        return config

    def get_prompt_template(self, template_name: str, **variables) -> str:
        """
        Get a prompt template and fill in variables

        Args:
            template_name: Name of the template (e.g., "parseTask")
            **variables: Variables to substitute in the template

        Returns:
            Formatted prompt string

        Example:
            prompt = loader.get_prompt_template("parseTask", input="Buy groceries")
        """
        if not self._prompts_config:
            raise ValueError("Prompts configuration not loaded")

        templates = self._prompts_config.get("templates", {})
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' not found")

        template_config = templates[template_name]
        template = template_config.get("template", "")

        # Substitute variables
        try:
            # Convert variables to strings and handle None values
            safe_vars = {}
            for key, value in variables.items():
                if value is None:
                    safe_vars[key] = ""
                elif isinstance(value, (dict, list)):
                    safe_vars[key] = json.dumps(value, indent=2)
                else:
                    safe_vars[key] = str(value)

            return template.format(**safe_vars)
        except KeyError as e:
            missing_var = str(e).strip("'")
            required_vars = template_config.get("variables", [])
            raise ValueError(
                f"Missing required variable '{missing_var}' for template '{template_name}'. "
                f"Required: {required_vars}"
            )

    def get_system_prompt(self, prompt_name: str) -> Dict[str, str]:
        """
        Get a system prompt

        Args:
            prompt_name: Name of the system prompt

        Returns:
            Dictionary with role and content
        """
        if not self._prompts_config:
            raise ValueError("Prompts configuration not loaded")

        system_prompts = self._prompts_config.get("systemPrompts", {})
        if prompt_name not in system_prompts:
            raise ValueError(f"System prompt '{prompt_name}' not found")

        return system_prompts[prompt_name]

    def get_escalation_keywords(self) -> list[str]:
        """Get list of keywords that trigger escalation to II-Agent"""
        if not self._prompts_config:
            return ["research", "analyze", "investigate", "summarize", "compare", "strategy"]
        keywords = self._prompts_config.get("escalationKeywords")
        if not keywords:
            return ["research", "analyze", "investigate", "summarize", "compare", "strategy"]
        if isinstance(keywords, list):
            return keywords
        return []

    def get_all_use_cases(self) -> list[str]:
        """Get list of all configured use cases"""
        if not self._models_config:
            return []
        return list(self._models_config.get("useCases", {}).keys())

    def get_all_providers(self) -> list[str]:
        """Get list of all configured providers"""
        if not self._models_config:
            return []
        return list(self._models_config.get("providers", {}).keys())


# Singleton instance
@lru_cache(maxsize=1)
def get_settings_loader() -> SettingsLoader:
    """Get or create the settings loader singleton"""
    return SettingsLoader()


# Convenience functions
def get_model_for_use_case(use_case: str, use_fallback: bool = True) -> str:
    """
    Convenience function to get model for a use case

    Args:
        use_case: The use case (e.g., "chat", "parseTask")
        use_fallback: Whether to use fallback if primary fails

    Returns:
        Model identifier string
    """
    return get_settings_loader().get_model_for_use_case(use_case, use_fallback)


def get_model_config(use_case: str) -> Dict[str, Any]:
    """
    Convenience function to get full model configuration

    Args:
        use_case: The use case

    Returns:
        Dictionary with model and parameters
    """
    return get_settings_loader().get_model_config(use_case)


def get_prompt_template(template_name: str, **variables) -> str:
    """
    Convenience function to get and format a prompt template

    Args:
        template_name: Name of the template
        **variables: Variables to substitute

    Returns:
        Formatted prompt string
    """
    return get_settings_loader().get_prompt_template(template_name, **variables)


def get_system_prompt(prompt_name: str) -> Dict[str, str]:
    """
    Convenience function to get a system prompt

    Args:
        prompt_name: Name of the system prompt

    Returns:
        Dictionary with role and content
    """
    return get_settings_loader().get_system_prompt(prompt_name)


def get_escalation_keywords() -> list[str]:
    """Get escalation keywords for II-Agent routing"""
    return get_settings_loader().get_escalation_keywords()


# Example usage
if __name__ == "__main__":
    # Test the settings loader
    loader = get_settings_loader()

    logger.info("=== Models Configuration ===")
    logger.debug(f"Chat model: {loader.get_model_for_use_case('chat')}")
    logger.debug(
        f"Orchestration model: {loader.get_model_for_use_case('orchestrateTask')}"
    )
    logger.debug(
        f"High reasoning model: {loader.get_model_for_use_case('highReasoning')}"
    )

    logger.info("=== Model Config ===")
    config = loader.get_model_config("chat")
    logger.debug(json.dumps(config, indent=2))

    logger.info("=== Prompt Template ===")
    prompt = loader.get_prompt_template("parseTask", input="Buy groceries tomorrow")
    logger.debug(prompt[:200] + "...")

    logger.info("=== Use Cases ===")
    logger.debug(f"Available use cases: {loader.get_all_use_cases()}")

    logger.info("=== Escalation Keywords ===")
    logger.debug(f"Keywords: {loader.get_escalation_keywords()}")
