"""Tests for SSE streaming utilities."""

import json

import pytest
from ai_core import StreamChunk
from ai_core.streaming.sse import (
    SSEEvent,
    create_sse_response_headers,
    format_sse_chunk,
    format_sse_event,
    parse_sse_event,
    stream_to_sse,
)


class TestSSEEvent:
    """Tests for SSEEvent model."""

    def test_default_event(self):
        """Test default SSE event."""
        event = SSEEvent()
        assert event.event_type == "token"
        assert event.content == ""
        assert event.data is None

    def test_custom_event(self):
        """Test custom SSE event."""
        event = SSEEvent(
            event_type="done",
            content="",
            data={"finish_reason": "stop"},
        )
        assert event.event_type == "done"
        assert event.data == {"finish_reason": "stop"}


class TestFormatSSEEvent:
    """Tests for format_sse_event function."""

    def test_format_token_event(self):
        """Test formatting a token event."""
        event = SSEEvent(event_type="token", content="Hello")
        result = format_sse_event(event)

        assert result.startswith("data: ")
        assert result.endswith("\n\n")

        # Parse the JSON
        data = json.loads(result[6:-2])
        assert data["type"] == "token"
        assert data["content"] == "Hello"

    def test_format_done_event(self):
        """Test formatting a done event."""
        event = SSEEvent(
            event_type="done",
            content="",
            data={"finish_reason": "stop", "tokens": 100},
        )
        result = format_sse_event(event)
        data = json.loads(result[6:-2])

        assert data["type"] == "done"
        assert data["content"] == ""
        assert data["finish_reason"] == "stop"
        assert data["tokens"] == 100

    def test_format_error_event(self):
        """Test formatting an error event."""
        event = SSEEvent(event_type="error", content="Connection failed")
        result = format_sse_event(event)
        data = json.loads(result[6:-2])

        assert data["type"] == "error"
        assert data["content"] == "Connection failed"


class TestFormatSSEChunk:
    """Tests for format_sse_chunk function."""

    def test_format_token_chunk(self):
        """Test formatting a token chunk."""
        chunk = StreamChunk(content="Hello", chunk_type="token")
        result = format_sse_chunk(chunk)
        data = json.loads(result[6:-2])

        assert data["type"] == "token"
        assert data["content"] == "Hello"
        assert "finish_reason" not in data

    def test_format_done_chunk_with_tokens(self):
        """Test formatting a done chunk with token counts."""
        chunk = StreamChunk(
            content="",
            chunk_type="done",
            finish_reason="stop",
            input_tokens=50,
            output_tokens=30,
        )
        result = format_sse_chunk(chunk)
        data = json.loads(result[6:-2])

        assert data["type"] == "done"
        assert data["finish_reason"] == "stop"
        assert data["input_tokens"] == 50
        assert data["output_tokens"] == 30


class TestParseSSEEvent:
    """Tests for parse_sse_event function."""

    def test_parse_token_event(self):
        """Test parsing a token event."""
        line = 'data: {"type": "token", "content": "Hello"}\n\n'
        event = parse_sse_event(line)

        assert event is not None
        assert event.event_type == "token"
        assert event.content == "Hello"

    def test_parse_done_event(self):
        """Test parsing a done event with extra data."""
        line = 'data: {"type": "done", "content": "", "finish_reason": "stop"}\n\n'
        event = parse_sse_event(line)

        assert event is not None
        assert event.event_type == "done"
        assert event.content == ""
        assert event.data == {"finish_reason": "stop"}

    def test_parse_invalid_format(self):
        """Test parsing invalid format returns None."""
        assert parse_sse_event("not a valid event") is None
        assert parse_sse_event("event: test") is None

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON returns None."""
        assert parse_sse_event("data: not json") is None
        assert parse_sse_event("data: {invalid}") is None


class TestStreamToSSE:
    """Tests for stream_to_sse function."""

    @pytest.mark.asyncio
    async def test_stream_tokens(self):
        """Test converting stream chunks to SSE."""
        async def mock_stream():
            yield StreamChunk(content="Hello", chunk_type="token")
            yield StreamChunk(content=" World", chunk_type="token")
            yield StreamChunk(content="", chunk_type="done", finish_reason="stop")

        results = []
        async for sse_line in stream_to_sse(mock_stream()):
            results.append(sse_line)

        assert len(results) == 3

        # First token
        data1 = json.loads(results[0][6:-2])
        assert data1["content"] == "Hello"

        # Second token
        data2 = json.loads(results[1][6:-2])
        assert data2["content"] == " World"

        # Done
        data3 = json.loads(results[2][6:-2])
        assert data3["type"] == "done"

    @pytest.mark.asyncio
    async def test_stream_error(self):
        """Test handling error in stream."""
        async def mock_stream():
            yield StreamChunk(content="Starting", chunk_type="token")
            yield StreamChunk(content="Error occurred", chunk_type="error")

        results = []
        async for sse_line in stream_to_sse(mock_stream()):
            results.append(sse_line)

        assert len(results) == 2

        # Error
        data = json.loads(results[1][6:-2])
        assert data["type"] == "error"
        assert data["content"] == "Error occurred"


class TestCreateSSEResponseHeaders:
    """Tests for create_sse_response_headers function."""

    def test_headers_content(self):
        """Test SSE response headers."""
        headers = create_sse_response_headers()

        assert headers["Content-Type"] == "text/event-stream"
        assert headers["Cache-Control"] == "no-cache"
        assert headers["Connection"] == "keep-alive"
        assert headers["X-Accel-Buffering"] == "no"

    def test_headers_are_dict(self):
        """Test headers return type."""
        headers = create_sse_response_headers()
        assert isinstance(headers, dict)
