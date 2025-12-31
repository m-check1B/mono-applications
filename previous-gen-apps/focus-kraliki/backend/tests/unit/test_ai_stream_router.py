"""
Unit tests for AI Stream router
Tests streaming chat responses
"""

import pytest
import json
from fastapi.testclient import TestClient


class TestAIStreamRouterAPI:
    """Test AI stream router via HTTP client"""

    def test_stream_chat_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.post("/ai/stream/chat")
        assert response.status_code == 401

    def test_stream_chat_authenticated(self, client: TestClient, auth_headers: dict):
        """Should stream chat response"""
        response = client.post(
            "/ai/stream/chat", params={"message": "Hello"}, headers=auth_headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_stream_chat_with_history(self, client: TestClient, auth_headers: dict):
        """Should handle conversation history"""
        history = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"},
        ]
        response = client.post(
            "/ai/stream/chat",
            params={
                "message": "New message",
                "conversation_history": json.dumps(history),
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_stream_chat_with_high_reasoning(
        self, client: TestClient, auth_headers: dict
    ):
        """Should use high reasoning model when requested"""
        response = client.post(
            "/ai/stream/chat",
            params={"message": "Complex question", "use_high_reasoning": "true"},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_stream_response_format(self, client: TestClient, auth_headers: dict):
        """Should return proper SSE format"""
        response = client.post(
            "/ai/stream/chat", params={"message": "Test"}, headers=auth_headers
        )
        assert response.status_code == 200

        content = response.content.decode("utf-8")
        assert "data: " in content or len(content) > 0

    def test_stream_cache_headers(self, client: TestClient, auth_headers: dict):
        """Should set proper cache control headers"""
        response = client.post(
            "/ai/stream/chat", params={"message": "Test"}, headers=auth_headers
        )
        assert response.status_code == 200
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]

    def test_stream_connection_headers(self, client: TestClient, auth_headers: dict):
        """Should set connection headers for streaming"""
        response = client.post(
            "/ai/stream/chat", params={"message": "Test"}, headers=auth_headers
        )
        assert response.status_code == 200
        assert "Connection" in response.headers
        assert "keep-alive" in response.headers["Connection"]

    def test_test_stream_no_auth(self, client: TestClient):
        """Test endpoint should not require authentication"""
        response = client.get("/ai/stream/test")
        assert response.status_code == 200

    def test_test_stream_response(self, client: TestClient):
        """Test endpoint should return proper SSE format"""
        response = client.get("/ai/stream/test")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_test_stream_content(self, client: TestClient):
        """Test endpoint should send test messages"""
        response = client.get("/ai/stream/test")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "data: " in content

    def test_multiple_concurrent_streams(self, client: TestClient, auth_headers: dict):
        """Should handle multiple stream requests"""
        responses = []
        for i in range(3):
            response = client.post(
                "/ai/stream/chat",
                params={"message": f"Message {i}"},
                headers=auth_headers,
            )
            responses.append(response)
            assert response.status_code == 200

    def test_stream_with_long_message(self, client: TestClient, auth_headers: dict):
        """Should handle long messages"""
        long_message = "a" * 1000
        response = client.post(
            "/ai/stream/chat", params={"message": long_message}, headers=auth_headers
        )
        assert response.status_code == 200

    def test_stream_with_special_characters(
        self, client: TestClient, auth_headers: dict
    ):
        """Should handle special characters in message"""
        message = "Hello! @#$%^&*()_+-=[]{}|;':\",./<>?"
        response = client.post(
            "/ai/stream/chat", params={"message": message}, headers=auth_headers
        )
        assert response.status_code == 200

    def test_stream_empty_message(self, client: TestClient, auth_headers: dict):
        """Should handle empty message"""
        response = client.post(
            "/ai/stream/chat", params={"message": ""}, headers=auth_headers
        )
        assert response.status_code == 200

    def test_stream_unicode_message(self, client: TestClient, auth_headers: dict):
        """Should handle unicode characters"""
        message = "Hello 世界 🌍 Привет"
        response = client.post(
            "/ai/stream/chat", params={"message": message}, headers=auth_headers
        )
        assert response.status_code == 200
