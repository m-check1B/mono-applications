"""Anthropic Claude provider implementation."""

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


class ClaudeProvider(BaseTextProvider):
    """Anthropic Claude text provider."""

    # Default models
    DEFAULT_MODEL = "claude-opus-4-20250514"
    MODELS = {
        "claude-opus-4-20250514": {"context": 200000, "tier": "premium"},
        "claude-3-5-haiku-20241022": {"context": 200000, "tier": "economy"},
        # Sonnet models removed - use Opus only
        # "claude-sonnet-4-20250514": {"context": 200000, "tier": "standard"},
        # "claude-3-5-sonnet-20241022": {"context": 200000, "tier": "standard"},
    }

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize Claude provider.

        Args:
            api_key: Anthropic API key
            model: Default model to use
        """
        super().__init__(api_key)
        self._model = model or self.DEFAULT_MODEL
        self._client = None

    def _get_client(self):
        """Lazy load the Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install ai-core[anthropic]"
                )
            self._client = Anthropic(api_key=self._api_key)
        return self._client

    @property
    def provider_type(self) -> LLMProvider:
        return LLMProvider.ANTHROPIC

    @property
    def capabilities(self) -> ProviderCapabilities:
        model_info = self.MODELS.get(self._model, {"context": 200000, "tier": "standard"})
        return ProviderCapabilities(
            supports_streaming=True,
            supports_system_prompt=True,
            supports_function_calling=True,
            max_context_length=model_info["context"],
            cost_tier=model_info["tier"],
        )

    def _convert_messages(self, messages: list[Message]) -> tuple[str | None, list[dict]]:
        """Convert messages to Anthropic format.

        Args:
            messages: List of Message objects

        Returns:
            Tuple of (system_prompt, messages_list)
        """
        system_prompt = None
        converted = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
            else:
                converted.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })

        return system_prompt, converted

    async def complete(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> CompletionResult:
        """Generate a completion using Claude.

        Args:
            messages: List of messages
            config: Completion configuration

        Returns:
            CompletionResult with the generated text
        """
        client = self._get_client()
        system_prompt, converted_messages = self._convert_messages(messages)

        # Use config system prompt if provided, otherwise use extracted
        if config.system_prompt:
            system_prompt = config.system_prompt

        model = config.model or self._model

        kwargs = {
            "model": model,
            "max_tokens": config.max_tokens,
            "messages": converted_messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt
        if config.temperature is not None:
            kwargs["temperature"] = config.temperature
        if config.top_p is not None:
            kwargs["top_p"] = config.top_p
        if config.stop_sequences:
            kwargs["stop_sequences"] = config.stop_sequences

        response = client.messages.create(**kwargs)

        return CompletionResult(
            content=response.content[0].text,
            model=model,
            provider=self.provider_type,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.stop_reason,
        )

    async def stream(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream a completion using Claude.

        Args:
            messages: List of messages
            config: Completion configuration

        Yields:
            StreamChunk for each token
        """
        client = self._get_client()
        system_prompt, converted_messages = self._convert_messages(messages)

        if config.system_prompt:
            system_prompt = config.system_prompt

        model = config.model or self._model

        kwargs = {
            "model": model,
            "max_tokens": config.max_tokens,
            "messages": converted_messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt
        if config.temperature is not None:
            kwargs["temperature"] = config.temperature
        if config.top_p is not None:
            kwargs["top_p"] = config.top_p
        if config.stop_sequences:
            kwargs["stop_sequences"] = config.stop_sequences

        try:
            with client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    if text:
                        yield StreamChunk(content=text, chunk_type="token")

            # Final message with usage
            final_message = stream.get_final_message()
            yield StreamChunk(
                content="",
                chunk_type="done",
                finish_reason=final_message.stop_reason if final_message else None,
                input_tokens=final_message.usage.input_tokens if final_message else None,
                output_tokens=final_message.usage.output_tokens if final_message else None,
            )

        except Exception as e:
            yield StreamChunk(content=str(e), chunk_type="error")


def create_claude_provider(api_key: str, model: str | None = None) -> ClaudeProvider:
    """Factory function to create a Claude provider.

    Args:
        api_key: Anthropic API key
        model: Default model to use

    Returns:
        Configured ClaudeProvider instance
    """
    return ClaudeProvider(api_key=api_key, model=model)
