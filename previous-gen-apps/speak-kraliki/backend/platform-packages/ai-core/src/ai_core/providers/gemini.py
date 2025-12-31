"""Google Gemini provider implementation."""

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


class GeminiProvider(BaseTextProvider):
    """Google Gemini text provider."""

    # Default models
    DEFAULT_MODEL = "gemini-2.5-flash"
    MODELS = {
        "gemini-2.5-flash": {"context": 1000000, "tier": "economy"},
        "gemini-2.5-pro": {"context": 1000000, "tier": "standard"},
        "gemini-1.5-flash": {"context": 1000000, "tier": "economy"},
        "gemini-1.5-pro": {"context": 2000000, "tier": "premium"},
    }

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize Gemini provider.

        Args:
            api_key: Google API key
            model: Default model to use
        """
        super().__init__(api_key)
        self._model = model or self.DEFAULT_MODEL
        self._client = None

    def _get_client(self):
        """Lazy load the Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError(
                    "google-generativeai package required. Install with: pip install ai-core[gemini]"
                )
            genai.configure(api_key=self._api_key)
            self._client = genai
        return self._client

    def _get_model(self, model_name: str):
        """Get a Gemini GenerativeModel instance."""
        genai = self._get_client()
        return genai.GenerativeModel(model_name)

    @property
    def provider_type(self) -> LLMProvider:
        return LLMProvider.GEMINI

    @property
    def capabilities(self) -> ProviderCapabilities:
        model_info = self.MODELS.get(self._model, {"context": 1000000, "tier": "standard"})
        return ProviderCapabilities(
            supports_streaming=True,
            supports_system_prompt=True,
            supports_function_calling=True,
            max_context_length=model_info["context"],
            cost_tier=model_info["tier"],
        )

    def _convert_messages(
        self, messages: list[Message], system_prompt: str | None = None
    ) -> tuple[str | None, list[dict]]:
        """Convert messages to Gemini format.

        Args:
            messages: List of Message objects
            system_prompt: Optional system prompt

        Returns:
            Tuple of (system_instruction, history)
        """
        system_instruction = system_prompt
        history = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                # Gemini uses system_instruction separately
                system_instruction = msg.content
            else:
                role = "user" if msg.role == MessageRole.USER else "model"
                history.append({
                    "role": role,
                    "parts": [msg.content],
                })

        return system_instruction, history

    async def complete(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> CompletionResult:
        """Generate a completion using Gemini.

        Args:
            messages: List of messages
            config: Completion configuration

        Returns:
            CompletionResult with the generated text
        """
        model_name = config.model or self._model
        system_instruction, history = self._convert_messages(messages, config.system_prompt)

        # Create model with system instruction
        genai = self._get_client()
        model_kwargs = {}
        if system_instruction:
            model_kwargs["system_instruction"] = system_instruction

        model = genai.GenerativeModel(model_name, **model_kwargs)

        # Configure generation
        generation_config = {
            "max_output_tokens": config.max_tokens,
        }
        if config.temperature is not None:
            generation_config["temperature"] = config.temperature
        if config.top_p is not None:
            generation_config["top_p"] = config.top_p
        if config.stop_sequences:
            generation_config["stop_sequences"] = config.stop_sequences

        # Build the prompt from history
        if len(history) == 1:
            # Single message - use generate_content directly
            response = model.generate_content(
                history[0]["parts"][0],
                generation_config=generation_config,
            )
        else:
            # Multi-turn - use chat
            chat = model.start_chat(history=history[:-1])
            last_message = history[-1]["parts"][0] if history else ""
            response = chat.send_message(last_message, generation_config=generation_config)

        # Extract token counts if available
        input_tokens = 0
        output_tokens = 0
        if hasattr(response, "usage_metadata"):
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)

        return CompletionResult(
            content=response.text,
            model=model_name,
            provider=self.provider_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=response.candidates[0].finish_reason.name if response.candidates else None,
        )

    async def stream(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream a completion using Gemini.

        Args:
            messages: List of messages
            config: Completion configuration

        Yields:
            StreamChunk for each token
        """
        model_name = config.model or self._model
        system_instruction, history = self._convert_messages(messages, config.system_prompt)

        genai = self._get_client()
        model_kwargs = {}
        if system_instruction:
            model_kwargs["system_instruction"] = system_instruction

        model = genai.GenerativeModel(model_name, **model_kwargs)

        generation_config = {
            "max_output_tokens": config.max_tokens,
        }
        if config.temperature is not None:
            generation_config["temperature"] = config.temperature
        if config.top_p is not None:
            generation_config["top_p"] = config.top_p
        if config.stop_sequences:
            generation_config["stop_sequences"] = config.stop_sequences

        try:
            # Build prompt
            if len(history) == 1:
                prompt = history[0]["parts"][0]
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    stream=True,
                )
            else:
                chat = model.start_chat(history=history[:-1])
                last_message = history[-1]["parts"][0] if history else ""
                response = chat.send_message(
                    last_message,
                    generation_config=generation_config,
                    stream=True,
                )

            finish_reason = None
            for chunk in response:
                if chunk.text:
                    yield StreamChunk(content=chunk.text, chunk_type="token")
                if chunk.candidates and chunk.candidates[0].finish_reason:
                    finish_reason = chunk.candidates[0].finish_reason.name

            # Get usage from final response if available
            input_tokens = None
            output_tokens = None
            if hasattr(response, "usage_metadata"):
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", None)

            yield StreamChunk(
                content="",
                chunk_type="done",
                finish_reason=finish_reason,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        except Exception as e:
            yield StreamChunk(content=str(e), chunk_type="error")


def create_gemini_provider(api_key: str, model: str | None = None) -> GeminiProvider:
    """Factory function to create a Gemini provider.

    Args:
        api_key: Google API key
        model: Default model to use

    Returns:
        Configured GeminiProvider instance
    """
    return GeminiProvider(api_key=api_key, model=model)
