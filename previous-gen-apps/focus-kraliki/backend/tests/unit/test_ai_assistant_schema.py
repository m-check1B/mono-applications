"""
AI Assistant Schema Tests
Test Pydantic schemas for AI assistant endpoints
"""

import pytest
from pydantic import ValidationError

from app.schemas.ai_assistant import (
    ChatMessage,
    AssistantLiveRequest,
    AssistantLiveResponse,
)


class TestChatMessage:
    """Tests for ChatMessage schema."""

    def test_chat_message_valid(self):
        """Test valid ChatMessage creation."""
        message = ChatMessage(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"

    def test_chat_message_assistant_role(self):
        """Test ChatMessage with assistant role."""
        message = ChatMessage(role="assistant", content="Response")
        assert message.role == "assistant"
        assert message.content == "Response"

    def test_chat_message_system_role(self):
        """Test ChatMessage with system role."""
        message = ChatMessage(role="system", content="Instructions")
        assert message.role == "system"
        assert message.content == "Instructions"


class TestAssistantLiveRequest:
    """Tests for AssistantLiveRequest schema."""

    def test_request_minimal(self):
        """Test minimal valid request."""
        request = AssistantLiveRequest(message="Hello AI")
        assert request.message == "Hello AI"
        assert request.conversationHistory == []
        assert request.context is None

    def test_request_with_history(self):
        """Test request with conversation history."""
        history = [
            ChatMessage(role="user", content="Previous question"),
            ChatMessage(role="assistant", content="Previous answer"),
        ]
        request = AssistantLiveRequest(
            message="Follow up question", conversationHistory=history
        )
        assert request.message == "Follow up question"
        assert len(request.conversationHistory) == 2
        assert request.conversationHistory[0].role == "user"

    def test_request_with_context(self):
        """Test request with context metadata."""
        context = {"user_id": "123", "session_id": "abc"}
        request = AssistantLiveRequest(message="Context aware message", context=context)
        assert request.message == "Context aware message"
        assert request.context == context
        assert request.context["user_id"] == "123"

    def test_request_complete(self):
        """Test complete request with all fields."""
        history = [
            ChatMessage(role="user", content="Q1"),
            ChatMessage(role="assistant", content="A1"),
        ]
        context = {"mode": "creative", "temperature": 0.8}

        request = AssistantLiveRequest(
            message="New question", conversationHistory=history, context=context
        )

        assert request.message == "New question"
        assert len(request.conversationHistory) == 2
        assert request.context["mode"] == "creative"
        assert request.context["temperature"] == 0.8

    def test_request_empty_history(self):
        """Test request with empty history list."""
        request = AssistantLiveRequest(message="Message", conversationHistory=[])
        assert request.message == "Message"
        assert request.conversationHistory == []

    def test_request_multiple_history_entries(self):
        """Test request with multiple history entries."""
        history = [ChatMessage(role="user", content=f"Q{i}") for i in range(5)]
        request = AssistantLiveRequest(
            message="Final question", conversationHistory=history
        )
        assert len(request.conversationHistory) == 5
        assert request.conversationHistory[4].content == "Q4"


class TestAssistantLiveResponse:
    """Tests for AssistantLiveResponse schema."""

    def test_response_minimal(self):
        """Test minimal valid response."""
        response = AssistantLiveResponse(response="AI response", model="gpt-4")
        assert response.response == "AI response"
        assert response.model == "gpt-4"
        assert response.toolCalls == []
        assert response.metadata is None

    def test_response_with_tool_calls(self):
        """Test response with tool calls."""
        tool_calls = [{"name": "search", "arguments": {"query": "test"}}]
        response = AssistantLiveResponse(
            response="I'll search for you", model="gpt-4", toolCalls=tool_calls
        )
        assert len(response.toolCalls) == 1
        assert response.toolCalls[0]["name"] == "search"
        assert response.toolCalls[0]["arguments"]["query"] == "test"

    def test_response_with_metadata(self):
        """Test response with metadata."""
        metadata = {"tokens_used": 150, "latency_ms": 234, "cost": 0.005}
        response = AssistantLiveResponse(
            response="Response", model="claude-3", metadata=metadata
        )
        assert response.metadata == metadata
        assert response.metadata["tokens_used"] == 150
        assert response.metadata["cost"] == 0.005

    def test_response_complete(self):
        """Test complete response with all fields."""
        tool_calls = [
            {"name": "search", "arguments": {"query": "test"}},
            {"name": "calculate", "arguments": {"expression": "1+1"}},
        ]
        metadata = {"tokens_used": 200, "model_version": "v1.0", "cached": False}

        response = AssistantLiveResponse(
            response="Complete response",
            model="gpt-4-turbo",
            toolCalls=tool_calls,
            metadata=metadata,
        )

        assert response.response == "Complete response"
        assert response.model == "gpt-4-turbo"
        assert len(response.toolCalls) == 2
        assert response.metadata["model_version"] == "v1.0"
        assert response.metadata["cached"] is False

    def test_response_empty_tool_calls(self):
        """Test response with empty tool calls list."""
        response = AssistantLiveResponse(
            response="No tools", model="gpt-3.5", toolCalls=[]
        )
        assert response.toolCalls == []

    def test_response_multiple_tool_calls(self):
        """Test response with multiple tool calls."""
        tool_calls = [
            {"name": f"tool{i}", "arguments": {"arg": f"value{i}"}} for i in range(3)
        ]
        response = AssistantLiveResponse(
            response="Using multiple tools", model="gpt-4", toolCalls=tool_calls
        )
        assert len(response.toolCalls) == 3
        assert response.toolCalls[2]["name"] == "tool2"


class TestSchemaIntegration:
    """Integration tests for schema validation."""

    def test_roundtrip_request_response(self):
        """Test request/response roundtrip."""
        # Create request
        history = [ChatMessage(role="user", content="Input")]
        request = AssistantLiveRequest(
            message="Test", conversationHistory=history, context={"key": "value"}
        )

        # Create response
        response = AssistantLiveResponse(
            response="Output", model="test-model", toolCalls=[], metadata={"test": True}
        )

        assert request.message == "Test"
        assert request.context["key"] == "value"
        assert response.response == "Output"
        assert response.metadata["test"] is True

    def test_message_in_history_and_request(self):
        """Test that ChatMessage works in both contexts."""
        msg1 = ChatMessage(role="user", content="User message")
        msg2 = ChatMessage(role="assistant", content="Assistant message")

        request = AssistantLiveRequest(message="New", conversationHistory=[msg1, msg2])

        assert request.conversationHistory[0].role == "user"
        assert request.conversationHistory[1].role == "assistant"
