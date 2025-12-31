"""
AI Provider Abstraction - No hardcoded models or prompts.

All configuration comes from:
1. Environment variables (config.py)
2. Prompts file (config/brain_prompts.json)

Supported providers:
- gemini: Google Gemini (default, cost-effective)
- anthropic: Claude (quality fallback)
- glm: GLM-4/ChatGLM (cost-effective, good for agent work)
- openrouter: User's choice of models

Policy: Never hardcode models or prompts in code.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import google.generativeai as genai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    genai = None

try:
    from anthropic import Anthropic  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    Anthropic = None

try:
    import httpx  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    httpx = None

from app.core.config import settings


class PromptLoader:
    """Load prompts from external JSON file - no hardcoding."""

    _cache: Optional[Dict[str, Any]] = None
    _cache_mtime: float = 0

    @classmethod
    def get_prompts(cls) -> Dict[str, Any]:
        """Load prompts, with hot-reload on file change."""
        prompts_path = Path(settings.BRAIN_PROMPTS_FILE)

        # Try relative to backend directory
        if not prompts_path.is_absolute():
            backend_dir = Path(__file__).parent.parent.parent
            prompts_path = backend_dir / settings.BRAIN_PROMPTS_FILE

        if not prompts_path.exists():
            # Return minimal defaults if file missing
            return {
                "capture": {"classify": "Classify: {input}"},
                "understand_goal": {"parse": "Parse: {goal}"},
                "ask": {"prompt": "Question: {question}"}
            }

        # Check if file changed (hot-reload)
        mtime = prompts_path.stat().st_mtime
        if cls._cache is None or mtime > cls._cache_mtime:
            with open(prompts_path, 'r') as f:
                cls._cache = json.load(f)
            cls._cache_mtime = mtime

        return cls._cache

    @classmethod
    def get(cls, category: str, key: str, **kwargs) -> str:
        """Get a prompt with variable substitution."""
        prompts = cls.get_prompts()
        template = prompts.get(category, {}).get(key, "")

        # Substitute variables
        for k, v in kwargs.items():
            template = template.replace(f"{{{k}}}", str(v))

        return template


class AIProvider:
    """
    Unified AI provider interface.

    Usage:
        provider = AIProvider()
        response = await provider.generate("Your prompt here")
    """

    def __init__(self,
                 model: Optional[str] = None,
                 provider: Optional[str] = None):
        """
        Initialize with model/provider from settings or override.

        Args:
            model: Override model name (default from settings)
            provider: Override provider (default from settings)
        """
        self.model = model or settings.BRAIN_MODEL
        self.provider = provider or settings.BRAIN_MODEL_PROVIDER
        self.fallback_model = settings.BRAIN_FALLBACK_MODEL
        self.fallback_provider = settings.BRAIN_FALLBACK_PROVIDER

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response using configured provider."""
        try:
            return await self._call_provider(
                self.provider, self.model, prompt, max_tokens
            )
        except Exception as e:
            # Try fallback
            if self.fallback_model and self.fallback_provider:
                return await self._call_provider(
                    self.fallback_provider, self.fallback_model, prompt, max_tokens
                )
            raise e

    async def _call_provider(self, provider: str, model: str,
                             prompt: str, max_tokens: int) -> str:
        """Call specific provider."""

        if provider == "gemini":
            return await self._call_gemini(model, prompt, max_tokens)
        elif provider == "anthropic":
            return await self._call_anthropic(model, prompt, max_tokens)
        elif provider == "glm":
            return await self._call_glm(model, prompt, max_tokens)
        elif provider == "openrouter":
            return await self._call_openrouter(model, prompt, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _call_gemini(self, model: str, prompt: str, max_tokens: int) -> str:
        """Call Google Gemini API."""
        if not isinstance(settings.GEMINI_API_KEY, str) or not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        if genai is None:
            raise ValueError("GEMINI SDK not installed")

        genai.configure(api_key=settings.GEMINI_API_KEY)

        gen_model = genai.GenerativeModel(model)
        response = gen_model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens
            )
        )

        return response.text

    async def _call_anthropic(self, model: str, prompt: str, max_tokens: int) -> str:
        """Call Anthropic Claude API."""
        if not isinstance(settings.ANTHROPIC_API_KEY, str) or not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        if Anthropic is None:
            raise ValueError("Anthropic SDK not installed")

        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    async def _call_glm(self, model: str, prompt: str, max_tokens: int) -> str:
        """Call GLM API (cost-effective, good for agent work)."""
        if not isinstance(settings.GLM_API_KEY, str) or not settings.GLM_API_KEY:
            raise ValueError("GLM_API_KEY not configured")
        if httpx is None:
            raise ValueError("httpx not installed")

        # GLM uses OpenAI-compatible API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GLM_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model or "glm-4",
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_openrouter(self, model: str, prompt: str, max_tokens: int) -> str:
        """Call OpenRouter API (user's choice of models)."""
        if not isinstance(settings.OPENROUTER_API_KEY, str) or not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not configured")
        if httpx is None:
            raise ValueError("httpx not installed")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


# Convenience functions
def get_prompt(category: str, key: str, **kwargs) -> str:
    """Get a prompt from the prompts file."""
    return PromptLoader.get(category, key, **kwargs)


def get_ai_provider(model: Optional[str] = None,
                    provider: Optional[str] = None) -> AIProvider:
    """Get an AI provider instance."""
    return AIProvider(model=model, provider=provider)
