"""
Unit tests for captures router
Tests content capture and AI processing endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestCapturesRouterAPI:
    """Test captures router via HTTP client"""

    def test_create_capture_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.post(
            "/captures", json={"source_type": "text", "content": "Test content"}
        )
        assert response.status_code == 401

    def test_create_text_capture(self, client: TestClient, auth_headers: dict):
        """Should create text capture"""
        capture_data = {
            "source_type": "text",
            "content": "This is a test note about an important meeting",
            "title": "Meeting Notes",
        }
        response = client.post("/captures", json=capture_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "source_type" in data
        assert "title" in data
        assert "processed" in data

    def test_create_url_capture(self, client: TestClient, auth_headers: dict):
        """Should create URL capture"""
        capture_data = {"source_type": "url", "content": "https://example.com/article"}
        response = client.post("/captures", json=capture_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["source_type"] == "url"

    def test_create_capture_with_context(self, client: TestClient, auth_headers: dict):
        """Should create capture with user context"""
        capture_data = {
            "source_type": "text",
            "content": "Test note",
            "context": "Working on project X",
        }
        response = client.post("/captures", json=capture_data, headers=auth_headers)
        assert response.status_code == 200

    def test_list_captures_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/captures")
        assert response.status_code == 401

    def test_list_captures_authenticated(self, client: TestClient, auth_headers: dict):
        """Should list captures for authenticated user"""
        response = client.get("/captures", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "captures" in data
        assert "total" in data

    def test_list_captures_with_limit(self, client: TestClient, auth_headers: dict):
        """Should respect limit parameter"""
        response = client.get("/captures?limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["captures"]) <= 5

    def test_list_captures_with_offset(self, client: TestClient, auth_headers: dict):
        """Should respect offset parameter"""
        response = client.get("/captures?offset=5", headers=auth_headers)
        assert response.status_code == 200

    def test_list_captures_with_time_filter(
        self, client: TestClient, auth_headers: dict
    ):
        """Should filter captures by time"""
        response = client.get("/captures?since_hours=24", headers=auth_headers)
        assert response.status_code == 200

    def test_get_capture_context_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/captures/context")
        assert response.status_code == 401

    def test_get_capture_context(self, client: TestClient, auth_headers: dict):
        """Should get capture context for AI"""
        response = client.get(
            "/captures/context?hours=24&max_captures=10", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "context_summary" in data
        assert "captures" in data
        assert "total_captures" in data

    def test_get_capture_unauthenticated(self, client: TestClient, generate_id):
        """Should return 401 when not authenticated"""
        response = client.get(f"/captures/{generate_id()}")
        assert response.status_code == 401

    def test_get_capture_authenticated(self, client: TestClient, auth_headers: dict):
        """Should get specific capture"""
        capture_data = {"source_type": "text", "content": "Test content"}
        create_response = client.post(
            "/captures", json=capture_data, headers=auth_headers
        )
        capture_id = create_response.json()["id"]

        response = client.get(f"/captures/{capture_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == capture_id

    def test_get_capture_not_found(
        self, client: TestClient, auth_headers: dict, generate_id
    ):
        """Should return 404 for non-existent capture"""
        response = client.get(f"/captures/{generate_id()}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_capture_unauthenticated(self, client: TestClient, generate_id):
        """Should return 401 when not authenticated"""
        response = client.delete(f"/captures/{generate_id()}")
        assert response.status_code == 401

    def test_delete_capture_authenticated(self, client: TestClient, auth_headers: dict):
        """Should delete capture"""
        capture_data = {"source_type": "text", "content": "Test content to delete"}
        create_response = client.post(
            "/captures", json=capture_data, headers=auth_headers
        )
        capture_id = create_response.json()["id"]

        response = client.delete(f"/captures/{capture_id}", headers=auth_headers)
        assert response.status_code == 200

    def test_delete_capture_not_found(
        self, client: TestClient, auth_headers: dict, generate_id
    ):
        """Should return 404 for non-existent capture"""
        response = client.delete(f"/captures/{generate_id()}", headers=auth_headers)
        assert response.status_code == 404

    def test_capture_processed_structure(self, client: TestClient, auth_headers: dict):
        """Should return processed capture with AI analysis"""
        capture_data = {
            "source_type": "text",
            "content": "This is important information about task management",
        }
        response = client.post("/captures", json=capture_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        processed = data["processed"]
        assert "summary" in processed
        assert "key_points" in processed
        assert "entities" in processed
        assert "suggested_tags" in processed
        assert "action_items" in processed

    def test_multiple_captures_pagination(self, client: TestClient, auth_headers: dict):
        """Should handle pagination for multiple captures"""
        for i in range(15):
            capture_data = {
                "source_type": "text",
                "content": f"Capture {i}",
                "title": f"Title {i}",
            }
            client.post("/captures", json=capture_data, headers=auth_headers)

        response = client.get("/captures?limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["captures"]) == 10
        assert data["total"] >= 15
