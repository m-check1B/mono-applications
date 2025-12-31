"""Contract compliance tests for API endpoints.

This test suite ensures that the frontend and backend speak the same language
by validating response schemas, endpoint availability, and data contracts.
"""

import json
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.sessions.models import SessionCreateRequest, SessionResponse, SessionStatus


client = TestClient(app)


class TestSessionsContract:
    """Test session management API contracts."""

    def test_create_session_contract(self):
        """Test POST /api/v1/sessions response contract."""
        request_data = {
            "provider_type": "openai",
            "provider_model": "gpt-4o-realtime-preview-2024-10-01",
            "strategy": "direct",
            "telephony_provider": "twilio",
            "phone_number": "+1234567890",
            "metadata": {"test": True}
        }

        response = client.post("/api/v1/sessions", json=request_data)
        
        # Check status code
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        # Validate response schema
        data = response.json()
        
        # Required fields
        required_fields = ["id", "provider_type", "provider_model", "strategy", "status", "created_at", "updated_at", "metadata"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(data["id"], str)
        assert isinstance(data["provider_type"], str)
        assert isinstance(data["provider_model"], str)
        assert isinstance(data["strategy"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        assert isinstance(data["metadata"], dict)
        
        # Validate status enum
        assert data["status"] in [status.value for status in SessionStatus]
        
        # Validate with Pydantic model
        try:
            SessionResponse(**data)
        except ValidationError as e:
            pytest.fail(f"Response does not match SessionResponse schema: {e}")

    def test_bootstrap_session_contract(self):
        """Test POST /api/v1/sessions/bootstrap response contract."""
        request_data = {
            "provider_type": "openai",
            "provider_model": "gpt-4o-realtime-preview-2024-10-01",
            "strategy": "direct",
            "telephony_provider": "twilio",
            "phone_number": "+1234567890"
        }

        response = client.post("/api/v1/sessions/bootstrap", json=request_data)
        
        # Check status code
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        # Validate response schema
        data = response.json()
        
        # Required fields
        required_fields = ["session_id", "websocket_url", "provider_type", "status", "metadata"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(data["session_id"], str)
        assert isinstance(data["websocket_url"], str)
        assert isinstance(data["provider_type"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["metadata"], dict)
        
        # Validate websocket URL format
        assert data["websocket_url"].startswith(("ws://", "wss://"))
        assert "/ws/sessions/" in data["websocket_url"]
        assert data["session_id"] in data["websocket_url"]

    def test_get_session_contract(self):
        """Test GET /api/v1/sessions/{session_id} response contract."""
        # First create a session
        create_response = client.post("/api/v1/sessions", json={
            "provider_type": "openai",
            "provider_model": "gpt-4o-realtime-preview-2024-10-01",
            "strategy": "direct"
        })
        
        if create_response.status_code in [200, 201]:
            session_data = create_response.json()
            session_id = session_data["id"]
            
            # Get the session
            response = client.get(f"/api/v1/sessions/{session_id}")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Validate response schema (same as create)
            data = response.json()
            required_fields = ["id", "provider_type", "provider_model", "strategy", "status", "created_at", "updated_at", "metadata"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            # Validate with Pydantic model
            try:
                SessionResponse(**data)
            except ValidationError as e:
                pytest.fail(f"Response does not match SessionResponse schema: {e}")

    def test_list_sessions_contract(self):
        """Test GET /api/v1/sessions response contract."""
        response = client.get("/api/v1/sessions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should have sessions field
        assert "sessions" in data, "Missing 'sessions' field"
        assert isinstance(data["sessions"], list), "sessions should be a list"
        
        # If there are sessions, validate their structure
        if data["sessions"]:
            for session in data["sessions"]:
                try:
                    SessionResponse(**session)
                except ValidationError as e:
                    pytest.fail(f"Session item does not match SessionResponse schema: {e}")

    def test_start_end_session_contract(self):
        """Test POST /api/v1/sessions/{session_id}/start and /end contracts."""
        # Create a session first
        create_response = client.post("/api/v1/sessions", json={
            "provider_type": "openai",
            "provider_model": "gpt-4o-realtime-preview-2024-10-01",
            "strategy": "direct"
        })
        
        if create_response.status_code in [200, 201]:
            session_data = create_response.json()
            session_id = session_data["id"]
            
            # Test start session
            start_response = client.post(f"/api/v1/sessions/{session_id}/start")
            assert start_response.status_code in [200, 202], f"Start failed: {start_response.status_code}"
            
            start_data = start_response.json()
            assert "message" in start_data, "Start response missing 'message' field"
            assert isinstance(start_data["message"], str), "Message should be a string"
            
            # Test end session
            end_response = client.post(f"/api/v1/sessions/{session_id}/end")
            assert end_response.status_code in [200, 202], f"End failed: {end_response.status_code}"
            
            end_data = end_response.json()
            assert "message" in end_data, "End response missing 'message' field"
            assert isinstance(end_data["message"], str), "Message should be a string"


class TestTelephonyContract:
    """Test telephony API contracts."""

    def test_telephony_providers_contract(self):
        """Test GET /api/telephony/providers response contract."""
        response = client.get("/api/telephony/providers")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Required fields
        required_fields = ["providers", "primary_provider", "fallback_providers"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(data["providers"], dict)
        assert isinstance(data["primary_provider"], str)
        assert isinstance(data["fallback_providers"], list)
        
        # Validate provider structure
        for provider_id, provider_info in data["providers"].items():
            assert isinstance(provider_id, str)
            assert isinstance(provider_info, dict)
            
            provider_fields = ["name", "is_configured", "capabilities", "is_primary"]
            for field in provider_fields:
                assert field in provider_info, f"Provider {provider_id} missing field: {field}"

    def test_telephony_stats_contract(self):
        """Test GET /api/telephony/stats response contract."""
        response = client.get("/api/telephony/stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Required fields
        required_fields = ["total_calls", "active_calls", "completed_calls", "providers", "calls_by_provider"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(data["total_calls"], int)
        assert isinstance(data["active_calls"], int)
        assert isinstance(data["completed_calls"], int)
        assert isinstance(data["providers"], int)
        assert isinstance(data["calls_by_provider"], dict)

    def test_make_call_contract(self):
        """Test POST /api/telephony/call response contract."""
        request_data = {
            "to": "+1234567890",
            "company_id": 1,
            "provider": "twilio",
            "metadata": {"test": True}
        }

        response = client.post("/api/telephony/call", json=request_data)
        
        # Should return 202 or 400 (if not configured)
        assert response.status_code in [202, 400], f"Expected 202/400, got {response.status_code}"
        
        if response.status_code == 202:
            data = response.json()
            
            # Required fields for successful call
            required_fields = ["success", "call_id", "status", "provider", "metadata"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            assert isinstance(data["success"], bool)
            assert isinstance(data["call_id"], str)
            assert isinstance(data["status"], str)
            assert isinstance(data["provider"], str)
            assert isinstance(data["metadata"], dict)


class TestProvidersContract:
    """Test providers API contracts."""

    def test_list_providers_contract(self):
        """Test GET /api/v1/providers response contract."""
        response = client.get("/api/v1/providers")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Required fields
        required_fields = ["providers", "telephony"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate data types
        assert isinstance(data["providers"], list)
        assert isinstance(data["telephony"], list)
        
        # Validate provider structure
        for provider in data["providers"]:
            assert isinstance(provider, dict)
            provider_fields = ["id", "name", "type", "is_configured", "capabilities"]
            for field in provider_fields:
                assert field in provider, f"Provider missing field: {field}"


class TestLegacyEndpointMapping:
    """Test that legacy endpoints still work or properly redirect."""

    def test_legacy_endpoints_compatibility(self):
        """Test that legacy endpoints are still accessible."""
        # Test some legacy endpoints that should still work
        legacy_endpoints = [
            "/health",
            "/",
            "/api/v1/providers"
        ]
        
        for endpoint in legacy_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Legacy endpoint {endpoint} failed: {response.status_code}"

    def test_error_response_contract(self):
        """Test that error responses follow consistent format."""
        # Test invalid session ID
        response = client.get("/api/v1/sessions/invalid-uuid")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        data = response.json()
        
        # Error responses should have detail field
        assert "detail" in data, "Error response missing 'detail' field"
        assert isinstance(data["detail"], str), "Error detail should be a string"


class TestWebSocketContract:
    """Test WebSocket endpoint contracts."""

    def test_websocket_endpoint_accessibility(self):
        """Test that WebSocket endpoints are accessible."""
        # We can't easily test WebSocket contracts with TestClient,
        # but we can verify the endpoint exists and accepts upgrade requests
        
        # Create a session first
        create_response = client.post("/api/v1/sessions", json={
            "provider_type": "openai",
            "provider_model": "gpt-4o-realtime-preview-2024-10-01",
            "strategy": "direct"
        })
        
        if create_response.status_code in [200, 201]:
            session_data = create_response.json()
            session_id = session_data["id"]
            
            # Test WebSocket endpoint (should return 426 Upgrade Required for HTTP request)
            response = client.get(f"/ws/sessions/{session_id}")
            assert response.status_code == 426, f"WebSocket endpoint should return 426 for HTTP requests"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])