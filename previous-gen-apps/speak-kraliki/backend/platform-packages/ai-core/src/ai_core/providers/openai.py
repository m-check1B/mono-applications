"""OpenAI provider implementation."""

from typing import AsyncGenerator

from ai_core.base import (
    BaseTextProvider,
    CompletionConfig,
    CompletionResult,
    LLMProvider,
    Message,
    MessageRole,
    ProviderCapabilities,
    StreamChunk,
)


class OpenAIProvider(BaseTextProvider):
    """OpenAI GPT text provider."""

    # Default models
    DEFAULT_MODEL = "gpt-4o"
    MODELS = {
        "gpt-4o": {"context": 128000, "tier": "standard"},
        "gpt-4o-mini": {"context": 128000, "tier": "economy"},
        "gpt-4-turbo": {"context": 128000, "tier": "premium"},
        "gpt-4": {"context": 8192, "tier": "premium"},
        "gpt-3.5-turbo": {"context": 16385, "tier": "economy"},
        "o1-preview": {"context": 128000, "tier": "reasoning"},
        "o1-mini": {"context": 128000, "tier": "reasoning"},
    }

    def __init__(
        self,
        api_key: str,
        model: str | None = None,
        base_url: str | None = None,
    ):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Default model to use
            base_url: Optional custom base URL (for OpenRouter, etc.)
        """
        super().__init__(api_key)
        self._model = model or self.DEFAULT_MODEL
        self._base_url = base_url
        self._client = None

    def _get_client(self):
        """Lazy load the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "openai package required. Install with: pip install ai-core[openai]"
                )
            kwargs = {"api_key": self._api_key}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = OpenAI(**kwargs)
        return self._client

    @property
    def provider_type(self) -> LLMProvider:
        return LLMProvider.OPENAI

    @property
    def capabilities(self) -> ProviderCapabilities:
        model_info = self.MODELS.get(self._model, {"context": 128000, "tier": "standard"})
        return ProviderCapabilities(
            supports_streaming=True,
            supports_system_prompt=True,
            supports_function_calling=True,
            max_context_length=model_info["context"],
            cost_tier=model_info["tier"],
        )

    def _convert_messages(
        self, messages: list[Message], system_prompt: str | None = None
    ) -> list[dict]:
        """Convert messages to OpenAI format.

        Args:
            messages: List of Message objects
            system_prompt: Optional system prompt to prepend

        Returns:
            List of message dicts in OpenAI format
        """
        converted = []

        if system_prompt:
            converted.append({"role": "system", "content": system_prompt})

        for msg in messages:
            converted.append({
                "role": msg.role.value,
                "content": msg.content,
            })

        return converted

    async def complete(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> CompletionResult:
        """Generate a completion using OpenAI.

        Args:
            messages: List of messages
            config: Completion configuration

        Returns:
            CompletionResult with the generated text
        """
        client = self._get_client()
        converted_messages = self._convert_messages(messages, config.system_prompt)
        model = config.model or self._model

        kwargs = {
            "model": model,
            "max_tokens": config.max_tokens,
            "messages": converted_messages,
        }

        if config.temperature is not None:
            kwargs["temperature"] = config.temperature
        if config.top_p is not None:
            kwargs["top_p"] = config.top_p
        if config.stop_sequences:
            kwargs["stop"] = config.stop_sequences

        response = client.chat.completions.create(**kwargs)

        return CompletionResult(
            content=response.choices[0].message.content or "",
            model=model,
            provider=self.provider_type,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            finish_reason=response.choices[0].finish_reason,
        )

    async def stream(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream a completion using OpenAI.

        Args:
            messages: List of messages
            config: Completion configuration

        Yields:
            StreamChunk for each token
        """
        client = self._get_client()
        converted_messages = self._convert_messages(messages, config.system_prompt)
        model = config.model or self._model

        kwargs = {
            "model": model,
            "max_tokens": config.max_tokens,
            "messages": converted_messages,
            "stream": True,
        }

        if config.temperature is not None:
            kwargs["temperature"] = config.temperature
        if config.top_p is not None:
            kwargs["top_p"] = config.top_p
        if config.stop_sequences:
            kwargs["stop"] = config.stop_sequences

        try:
            stream = client.chat.completions.create(**kwargs)

            finish_reason = None
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        chunk_type="token",
                    )
                if chunk.choices and chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason

            yield StreamChunk(
                content="",
                chunk_type="done",
                finish_reason=finish_reason,
            )

        except Exception as e:
            yield StreamChunk(content=str(e), chunk_type="error")


def create_openai_provider(
    api_key: str,
    model: str | None = None,
    base_url: str | None = None,
) -> OpenAIProvider:
    """Factory function to create an OpenAI provider.

    Args:
        api_key: OpenAI API key
        model: Default model to use
        base_url: Optional custom base URL

    Returns:
        Configured OpenAIProvider instance
    """
    return OpenAIProvider(api_key=api_key, model=model, base_url=base_url)
