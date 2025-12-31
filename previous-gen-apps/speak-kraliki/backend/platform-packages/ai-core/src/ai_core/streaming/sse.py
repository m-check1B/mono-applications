"""Server-Sent Events (SSE) formatting utilities.

This module provides utilities for formatting LLM streaming responses
as Server-Sent Events for web clients.
"""

import json
from typing import Any, AsyncGenerator

from pydantic import BaseModel

from ai_core.base import StreamChunk


class SSEEvent(BaseModel):
    """A Server-Sent Event."""
    event_type: str = "token"  # token, done, error
    content: str = ""
    data: dict[str, Any] | None = None


def format_sse_event(event: SSEEvent) -> str:
    """Format an SSE event as a string.

    Args:
        event: SSEEvent to format

    Returns:
        Formatted SSE string ready for streaming
    """
    payload = {
        "type": event.event_type,
        "content": event.content,
    }
    if event.data:
        payload.update(event.data)

    return f"data: {json.dumps(payload)}\n\n"


def format_sse_chunk(chunk: StreamChunk) -> str:
    """Format a StreamChunk as an SSE event string.

    Args:
        chunk: StreamChunk from a provider

    Returns:
        Formatted SSE string
    """
    payload = {
        "type": chunk.chunk_type,
        "content": chunk.content,
    }

    if chunk.finish_reason:
        payload["finish_reason"] = chunk.finish_reason
    if chunk.input_tokens is not None:
        payload["input_tokens"] = chunk.input_tokens
    if chunk.output_tokens is not None:
        payload["output_tokens"] = chunk.output_tokens

    return f"data: {json.dumps(payload)}\n\n"


def parse_sse_event(line: str) -> SSEEvent | None:
    """Parse an SSE event from a string.

    Args:
        line: SSE formatted line (data: {...})

    Returns:
        Parsed SSEEvent or None if invalid
    """
    if not line.startswith("data: "):
        return None

    try:
        data = json.loads(line[6:].strip())
        return SSEEvent(
            event_type=data.get("type", "token"),
            content=data.get("content", ""),
            data={k: v for k, v in data.items() if k not in ("type", "content")},
        )
    except json.JSONDecodeError:
        return None


async def stream_to_sse(
    stream: AsyncGenerator[StreamChunk, None]
) -> AsyncGenerator[str, None]:
    """Convert a StreamChunk generator to SSE strings.

    Args:
        stream: AsyncGenerator of StreamChunks

    Yields:
        SSE formatted strings
    """
    async for chunk in stream:
        yield format_sse_chunk(chunk)


def create_sse_response_headers() -> dict[str, str]:
    """Create standard headers for SSE responses.

    Returns:
        Dictionary of HTTP headers for SSE streaming
    """
    return {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # Disable nginx buffering
    }
