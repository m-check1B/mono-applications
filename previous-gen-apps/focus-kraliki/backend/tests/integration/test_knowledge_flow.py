"""
Knowledge Flow Integration Tests
Tests for Knowledge CRUD operations and AI chat functionality.
Target Coverage: 95%
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from unittest.mock import patch
import json

from app.models.user import User
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem


class TestKnowledgeTypeCRUD:
    """Test knowledge item type CRUD operations."""

    @pytest.mark.asyncio
    async def test_list_item_types_creates_defaults(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Test that listing item types creates default types on first access."""
        # Verify no types exist yet
        existing_types = (
            db.query(ItemType).filter(ItemType.userId == test_user.id).count()
        )
        assert existing_types == 0

        # List types (should trigger creation)
        response = await async_client.get("/knowledge/item-types", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have 4 default types
        assert data["total"] == 4
        assert len(data["itemTypes"]) == 4

        # Verify default types
        type_names = {t["name"] for t in data["itemTypes"]}
        assert type_names == {"Ideas", "Notes", "Tasks", "Plans"}

    @pytest.mark.asyncio
    async def test_create_custom_item_type(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
    ):
        """Test creating a custom item type."""
        response = await async_client.post(
            "/knowledge/item-types",
            json={"name": "Research", "icon": "🔬", "color": "#9333EA"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Research"
        assert data["icon"] == "🔬"
        assert data["color"] == "#9333EA"
        assert data["userId"] == test_user_with_knowledge_types.id

    @pytest.mark.asyncio
    async def test_get_item_type(
        self, async_client: AsyncClient, auth_headers: dict, knowledge_type_ids: dict
    ):
        """Test retrieving a specific item type."""
        ideas_id = knowledge_type_ids["Ideas"]

        response = await async_client.get(
            f"/knowledge/item-types/{ideas_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == ideas_id
        assert data["name"] == "Ideas"

    @pytest.mark.asyncio
    async def test_update_item_type(
        self, async_client: AsyncClient, auth_headers: dict, knowledge_type_ids: dict
    ):
        """Test updating an item type."""
        notes_id = knowledge_type_ids["Notes"]

        response = await async_client.patch(
            f"/knowledge/item-types/{notes_id}",
            json={"color": "#FF5733"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == notes_id
        assert data["color"] == "#FF5733"
        assert data["name"] == "Notes"  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_item_type(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        knowledge_type_ids: dict,
        db: Session,
    ):
        """Test deleting an item type cascades to knowledge items."""
        tasks_id = knowledge_type_ids["Tasks"]

        # Create a knowledge item of this type
        await async_client.post(
            "/knowledge/items",
            json={
                "typeId": tasks_id,
                "title": "Test Task",
                "content": "This should be deleted",
            },
            headers=auth_headers,
        )

        # Delete the type
        response = await async_client.delete(
            f"/knowledge/item-types/{tasks_id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify type is deleted
        deleted_type = db.query(ItemType).filter(ItemType.id == tasks_id).first()
        assert deleted_type is None

        # Verify associated items are deleted (cascade)
        orphaned_items = (
            db.query(KnowledgeItem).filter(KnowledgeItem.typeId == tasks_id).count()
        )
        assert orphaned_items == 0

    @pytest.mark.asyncio
    async def test_cannot_get_other_user_type(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_2: User,
        db: Session,
    ):
        """Test that users cannot access other users' item types."""
        # Create type for user 2
        from app.core.security import generate_id

        other_type = ItemType(
            id=generate_id(), userId=test_user_2.id, name="Private Type", icon="🔒"
        )
        db.add(other_type)
        db.commit()

        # Try to access with user 1's token
        response = await async_client.get(
            f"/knowledge/item-types/{other_type.id}", headers=auth_headers
        )

        assert response.status_code == 404


class TestKnowledgeItemCRUD:
    """Test knowledge item CRUD operations."""

    @pytest.mark.asyncio
    async def test_search_knowledge_items(
        self, async_client: AsyncClient, auth_headers: dict, knowledge_type_ids: dict
    ):
        """Test searching knowledge items."""
        ideas_id = knowledge_type_ids["Ideas"]

        # Create items
        await async_client.post(
            "/knowledge/items",
            json={
                "typeId": ideas_id,
                "title": "Python Tutorial",
                "content": "Learn Python programming",
            },
            headers=auth_headers,
        )
        await async_client.post(
            "/knowledge/items",
            json={
                "typeId": ideas_id,
                "title": "JavaScript Guide",
                "content": "Master JavaScript",
            },
            headers=auth_headers,
        )

        # Search for "Python"
        response = await async_client.get(
            "/knowledge/search?query=Python", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert "Python" in data["items"][0]["title"]

    @pytest.mark.asyncio
    async def test_search_knowledge_items_pagination(
        self, async_client: AsyncClient, auth_headers: dict, knowledge_type_ids: dict
    ):
        """Test pagination on knowledge items search."""
        ideas_id = knowledge_type_ids["Ideas"]

        # Create 5 items with "test" in title
        for i in range(5):
            await async_client.post(
                "/knowledge/items",
                json={
                    "typeId": ideas_id,
                    "title": f"test item {i}",
                    "content": f"test content {i}",
                },
                headers=auth_headers,
            )

        # First page (limit 2, offset 0)
        response = await async_client.get(
            "/knowledge/search?query=test&limit=2&offset=0", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["offset"] == 0
        assert data["limit"] == 2

        # Second page (limit 2, offset 2)
        response = await async_client.get(
            "/knowledge/search?query=test&limit=2&offset=2", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["offset"] == 2

        # Third page (limit 2, offset 4)
        response = await async_client.get(
            "/knowledge/search?query=test&limit=2&offset=4", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 1
        assert data["offset"] == 4


class TestKnowledgeAIChat:
    """Test AI-powered knowledge chat with function calling."""

    @pytest.mark.asyncio
    async def test_ai_chat_basic_response(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
        mock_openrouter,
    ):
        """Test basic AI chat without tool calls."""
        with patch(
            "app.routers.knowledge_ai.get_openrouter_client",
            return_value=mock_openrouter,
        ):
            response = await async_client.post(
                "/knowledge-ai/chat",
                json={
                    "message": "Hello, how can you help me?",
                    "conversationHistory": [],
                },
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            assert "response" in data
            assert data["model"] == "google/gemini-2.5-flash-preview-09-2025"

    @pytest.mark.asyncio
    async def test_ai_chat_creates_knowledge_item(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
        db: Session,
    ):
        """Test AI chat creating knowledge item via function calling."""
        # Get Ideas type ID
        ideas_type = (
            db.query(ItemType)
            .filter(
                ItemType.userId == test_user_with_knowledge_types.id,
                ItemType.name == "Ideas",
            )
            .first()
        )

        # Mock OpenRouter to simulate tool calling
        with patch("app.routers.knowledge_ai.get_openrouter_client") as mock_get_client:
            # Setup mock responses
            mock_client = mock_get_client.return_value

            # First call: AI decides to create item
            mock_tool_call = type(
                "obj",
                (object,),
                {
                    "id": "call_123",
                    "type": "function",
                    "function": type(
                        "obj",
                        (object,),
                        {
                            "name": "create_knowledge_item",
                            "arguments": json.dumps(
                                {
                                    "typeId": ideas_type.id,
                                    "title": "AI-Generated Idea",
                                    "content": "This was created by AI",
                                }
                            ),
                        },
                    )(),
                },
            )()

            first_message = type(
                "obj", (object,), {"content": None, "tool_calls": [mock_tool_call]}
            )()

            first_choice = type("obj", (object,), {"message": first_message})()

            first_completion = type("obj", (object,), {"choices": [first_choice]})()

            # Second call: AI responds after tool execution
            second_message = type(
                "obj",
                (object,),
                {"content": "I've created the idea for you!", "tool_calls": None},
            )()

            second_choice = type("obj", (object,), {"message": second_message})()

            second_completion = type("obj", (object,), {"choices": [second_choice]})()

            mock_client.chat.completions.create.side_effect = [
                first_completion,
                second_completion,
            ]

            # Make chat request
            response = await async_client.post(
                "/knowledge-ai/chat",
                json={
                    "message": "Create an idea called 'AI-Generated Idea'",
                    "conversationHistory": [],
                },
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response
            assert "I've created" in data["response"]
            assert len(data["toolCalls"]) == 1
            assert data["toolCalls"][0]["function"] == "create_knowledge_item"

            # Verify item was created in database
            created_item = (
                db.query(KnowledgeItem)
                .filter(KnowledgeItem.title == "AI-Generated Idea")
                .first()
            )

            assert created_item is not None
            assert created_item.content == "This was created by AI"

    @pytest.mark.asyncio
    async def test_ai_chat_usage_tracking_free_tier(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
        db: Session,
        mock_openrouter,
    ):
        """Test usage tracking for free tier users."""
        # Ensure user is not premium and has no custom key
        test_user_with_knowledge_types.isPremium = False
        test_user_with_knowledge_types.openRouterApiKey = None
        test_user_with_knowledge_types.usageCount = 0
        db.commit()

        with patch(
            "app.routers.knowledge_ai.get_openrouter_client",
            return_value=mock_openrouter,
        ):
            response = await async_client.post(
                "/knowledge-ai/chat",
                json={"message": "Hello", "conversationHistory": []},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Verify usage was tracked
            assert data["usageCount"] == 1
            assert data["remainingUsage"] == 99

            # Verify database was updated
            db.refresh(test_user_with_knowledge_types)
            assert test_user_with_knowledge_types.usageCount == 1

    @pytest.mark.asyncio
    async def test_ai_chat_free_tier_limit_reached(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
        db: Session,
    ):
        """Test that free tier users are blocked after reaching limit."""
        # Set user at limit
        test_user_with_knowledge_types.isPremium = False
        test_user_with_knowledge_types.openRouterApiKey = None
        test_user_with_knowledge_types.usageCount = 100
        db.commit()

        response = await async_client.post(
            "/knowledge-ai/chat",
            json={"message": "This should fail", "conversationHistory": []},
            headers=auth_headers,
        )

        assert response.status_code == 402
        assert "Free tier limit reached" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_ai_chat_byok_no_usage_tracking(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User,
        db: Session,
        mock_openrouter,
    ):
        """Test that BYOK users don't have usage tracked."""
        # Set user with custom API key
        test_user_with_knowledge_types.openRouterApiKey = "sk-custom-key-123"
        test_user_with_knowledge_types.usageCount = 0
        db.commit()

        with patch(
            "app.routers.knowledge_ai.get_openrouter_client",
            return_value=mock_openrouter,
        ):
            response = await async_client.post(
                "/knowledge-ai/chat",
                json={"message": "Hello", "conversationHistory": []},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()

            # Usage should not be tracked for BYOK
            assert data["usageCount"] is None
            assert data["remainingUsage"] is None

            # Verify database was NOT updated
            db.refresh(test_user_with_knowledge_types)
            assert test_user_with_knowledge_types.usageCount == 0
