"""
Unit tests for AI File Search router
Tests semantic search and File Search integration
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock


class TestAIFileSearchRouterAPI:
    """Test AI File Search router via HTTP client"""

    def test_query_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.post("/ai/file-search/query", json={"query": "test"})
        assert response.status_code == 401

    def test_query_authenticated(self, client: TestClient, auth_headers: dict):
        """Should handle semantic search query"""
        with patch(
            "app.routers.ai_file_search.query_store", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = {
                "answer": "Test answer",
                "citations": [],
                "model": "gemini-2.0-flash-exp",
                "store_name": "test-store",
            }

            response = client.post(
                "/ai/file-search/query",
                json={
                    "query": "What are the main tasks?",
                    "context": {"filter_by_type": "Tasks"},
                },
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "citations" in data
            assert "model" in data

    def test_query_with_empty_context(self, client: TestClient, auth_headers: dict):
        """Should handle query without context"""
        with patch(
            "app.routers.ai_file_search.query_store", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = {
                "answer": "Answer",
                "citations": [],
                "model": "gemini-2.0-flash-exp",
                "store_name": "test-store",
            }

            response = client.post(
                "/ai/file-search/query",
                json={"query": "test query"},
                headers=auth_headers,
            )
            assert response.status_code == 200

    def test_query_error_handling(self, client: TestClient, auth_headers: dict):
        """Should handle query errors gracefully"""
        with patch(
            "app.routers.ai_file_search.query_store", new_callable=AsyncMock
        ) as mock_query:
            mock_query.side_effect = Exception("API error")

            response = client.post(
                "/ai/file-search/query", json={"query": "test"}, headers=auth_headers
            )
            assert response.status_code == 500

    def test_status_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/ai/file-search/status")
        assert response.status_code == 401

    def test_status_authenticated(self, client: TestClient, auth_headers: dict):
        """Should return File Search status"""
        with patch("app.routers.ai_file_search.is_gemini_available") as mock_available:
            mock_available.return_value = True

            response = client.get("/ai/file-search/status", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert "store_exists" in data
            assert "gemini_available" in data

    def test_status_without_store(self, client: TestClient, auth_headers: dict):
        """Should return status when no store exists"""
        with patch("app.routers.ai_file_search.is_gemini_available") as mock_available:
            mock_available.return_value = True

            response = client.get("/ai/file-search/status", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["store_exists"] is False

    def test_import_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.post(
            "/ai/file-search/import", json={"knowledge_item_id": "test-id"}
        )
        assert response.status_code == 401

    def test_import_with_invalid_item(self, client: TestClient, auth_headers: dict):
        """Should return 404 for non-existent knowledge item"""
        with patch("app.routers.ai_file_search.is_gemini_available") as mock_available:
            mock_available.return_value = True

            response = client.post(
                "/ai/file-search/import",
                json={"knowledge_item_id": "non-existent-id"},
                headers=auth_headers,
            )
            assert response.status_code == 404

    def test_import_unavailable_gemini(self, client: TestClient, auth_headers: dict, test_user, db):
        """Should return 503 when Gemini is unavailable"""
        from app.models.knowledge_item import KnowledgeItem
        from app.models.item_type import ItemType
        from app.core.security_v2 import generate_id

        # Create item type first
        item_type = ItemType(
            id="test-note",
            userId=test_user.id,
            name="Test Note",
            icon="file-text"
        )
        db.add(item_type)

        # Create a knowledge item for this user
        knowledge_item = KnowledgeItem(
            id=generate_id(),
            userId=test_user.id,
            typeId="test-note",
            title="Test Item",
            content="Test content",
            completed=False
        )
        db.add(knowledge_item)
        db.commit()

        with patch("app.routers.ai_file_search.is_gemini_available") as mock_available:
            mock_available.return_value = False

            response = client.post(
                "/ai/file-search/import",
                json={"knowledge_item_id": knowledge_item.id},
                headers=auth_headers,
            )
            assert response.status_code == 503

    def test_documents_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/ai/file-search/documents")
        assert response.status_code == 401

    def test_documents_authenticated(self, client: TestClient, auth_headers: dict):
        """Should list File Search documents"""
        with (
            patch("app.routers.ai_file_search.is_gemini_available") as mock_available,
            patch(
                "app.routers.ai_file_search.get_or_create_org_store",
                new_callable=AsyncMock,
            ) as mock_store,
            patch(
                "app.routers.ai_file_search.list_store_documents",
                new_callable=AsyncMock,
            ) as mock_docs,
        ):
            mock_available.return_value = True
            mock_store.return_value = "test-store"
            mock_docs.return_value = [
                {
                    "name": "file1",
                    "display_name": "File 1",
                    "size_bytes": 1024,
                    "create_time": "2024-01-01",
                }
            ]

            response = client.get(
                "/ai/file-search/documents?limit=10", headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "documents" in data
            assert "total" in data

    def test_documents_unavailable_gemini(self, client: TestClient, auth_headers: dict):
        """Should return 503 when Gemini is unavailable"""
        with patch("app.routers.ai_file_search.is_gemini_available") as mock_available:
            mock_available.return_value = False

            response = client.get("/ai/file-search/documents", headers=auth_headers)
            assert response.status_code == 503

    def test_documents_with_limit(self, client: TestClient, auth_headers: dict):
        """Should respect limit parameter"""
        with (
            patch("app.routers.ai_file_search.is_gemini_available") as mock_available,
            patch(
                "app.routers.ai_file_search.get_or_create_org_store",
                new_callable=AsyncMock,
            ) as mock_store,
            patch(
                "app.routers.ai_file_search.list_store_documents",
                new_callable=AsyncMock,
            ) as mock_docs,
        ):
            mock_available.return_value = True
            mock_store.return_value = "test-store"
            mock_docs.return_value = []

            response = client.get(
                "/ai/file-search/documents?limit=50", headers=auth_headers
            )
            assert response.status_code == 200

    def test_health_check_no_auth(self, client: TestClient):
        """Health check should not require authentication"""
        response = client.get("/ai/file-search/health")
        assert response.status_code == 200
        data = response.json()
        assert "gemini_available" in data
        assert "api_key_configured" in data
        assert "service" in data
        assert "status" in data

    def test_health_check_response_structure(self, client: TestClient):
        """Health check should return proper structure"""
        with patch("app.routers.ai_file_search.is_gemini_available") as mock_available:
            mock_available.return_value = False

            response = client.get("/ai/file-search/health")
            assert response.status_code == 200
            data = response.json()

            assert isinstance(data["gemini_available"], bool)
            assert isinstance(data["api_key_configured"], bool)
            assert data["service"] == "File Search"
            assert data["status"] in ["healthy", "degraded"]
