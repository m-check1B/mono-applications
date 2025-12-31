"""MCP Tools for ai-core LLM providers.

These tools expose ai-core functionality through the Model Context Protocol,
allowing AI agents to use LLM providers as tools.
"""

from dataclasses import dataclass
from typing import Any, Optional

from pydantic import BaseModel, Field


class CompletionToolInput(BaseModel):
    """Input schema for completion tool."""
    prompt: str = Field(..., description="The prompt or message to send to the LLM")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")
    model: Optional[str] = Field(None, description="Model override (uses default if not specified)")
    max_tokens: int = Field(2000, description="Maximum tokens to generate", ge=1, le=100000)
    temperature: float = Field(0.7, description="Sampling temperature", ge=0.0, le=2.0)


class StreamingCompletionToolInput(BaseModel):
    """Input schema for streaming completion tool."""
    prompt: str = Field(..., description="The prompt or message to send to the LLM")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")
    model: Optional[str] = Field(None, description="Model override (uses default if not specified)")
    max_tokens: int = Field(2000, description="Maximum tokens to generate", ge=1, le=100000)
    temperature: float = Field(0.7, description="Sampling temperature", ge=0.0, le=2.0)


class ProviderInfoToolInput(BaseModel):
    """Input schema for provider info tool."""
    include_capabilities: bool = Field(True, description="Include detailed capabilities")


@dataclass
class CompletionTool:
    """MCP Tool: Generate text completion using configured LLM provider."""
    name: str = "ai_core_complete"
    description: str = "Generate text completion using configured LLM provider (Claude, OpenAI, Gemini)"
    input_schema: type = CompletionToolInput


@dataclass
class StreamingCompletionTool:
    """MCP Tool: Stream text completion using configured LLM provider."""
    name: str = "ai_core_stream"
    description: str = "Stream text completion tokens from configured LLM provider"
    input_schema: type = StreamingCompletionToolInput


@dataclass
class ProviderInfoTool:
    """MCP Tool: Get information about the configured LLM provider."""
    name: str = "ai_core_provider_info"
    description: str = "Get information about the configured LLM provider and its capabilities"
    input_schema: type = ProviderInfoToolInput
