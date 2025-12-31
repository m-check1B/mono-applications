import pytest
from unittest.mock import MagicMock, patch
from app.services.knowledge_defaults import (
    ensure_default_item_types,
    DEFAULT_ITEM_TYPES,
)


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user_id():
    return "test-user-123"


class TestKnowledgeDefaults:
    def test_default_item_types_structure(self):
        """Test that DEFAULT_ITEM_TYPES is properly structured."""
        assert len(DEFAULT_ITEM_TYPES) == 4
        assert all("name" in t for t in DEFAULT_ITEM_TYPES)
        assert all("icon" in t for t in DEFAULT_ITEM_TYPES)
        assert all("color" in t for t in DEFAULT_ITEM_TYPES)

    def test_ensure_default_item_types_existing(self, mock_db, mock_user_id):
        """Test that existing item types are returned without creating new ones."""
        existing_types = [MagicMock()]
        mock_db.query.return_value.filter.return_value.all.return_value = existing_types

        result = ensure_default_item_types(mock_user_id, mock_db)

        assert result == existing_types
        mock_db.query.assert_called_once()
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    @patch("app.services.knowledge_defaults.ItemType")
    @patch("app.services.knowledge_defaults.generate_id")
    def test_ensure_default_item_types_creates_defaults(
        self, mock_gen_id, mock_item_type_class, mock_db, mock_user_id
    ):
        """Test that default item types are created when user has none."""
        mock_gen_id.side_effect = ["type-1", "type-2", "type-3", "type-4"]
        mock_db.query.return_value.filter.return_value.all.return_value = []

        created_items = []

        def mock_item_type(**kwargs):
            mock_item = MagicMock()
            mock_item.__dict__.update(kwargs)
            created_items.append(kwargs)
            return mock_item

        mock_item_type_class.side_effect = mock_item_type

        result = ensure_default_item_types(mock_user_id, mock_db)

        assert mock_db.add.call_count == 4
        mock_db.commit.assert_called_once()
        mock_db.refresh.call_count == 4

        assert len(created_items) == 4
        for i, item_kwargs in enumerate(created_items):
            assert item_kwargs["userId"] == mock_user_id
            assert item_kwargs["name"] == DEFAULT_ITEM_TYPES[i]["name"]
            assert item_kwargs["icon"] == DEFAULT_ITEM_TYPES[i]["icon"]
            assert item_kwargs["color"] == DEFAULT_ITEM_TYPES[i]["color"]

    @patch("app.services.knowledge_defaults.ItemType")
    @patch("app.services.knowledge_defaults.generate_id")
    def test_ensure_default_item_types_names(
        self, mock_gen_id, mock_item_type_class, mock_db, mock_user_id
    ):
        """Test that default item types have correct names."""
        mock_gen_id.side_effect = ["type-1", "type-2", "type-3", "type-4"]
        mock_db.query.return_value.filter.return_value.all.return_value = []

        def mock_item_type(**kwargs):
            mock_item = MagicMock()
            mock_item.__dict__.update(kwargs)
            return mock_item

        mock_item_type_class.side_effect = mock_item_type

        result = ensure_default_item_types(mock_user_id, mock_db)

        names = [t.name for t in result]
        expected_names = ["Ideas", "Notes", "Tasks", "Plans"]
        assert names == expected_names

    @patch("app.services.knowledge_defaults.ItemType")
    @patch("app.services.knowledge_defaults.generate_id")
    def test_ensure_default_item_types_icons(
        self, mock_gen_id, mock_item_type_class, mock_db, mock_user_id
    ):
        """Test that default item types have correct icons."""
        mock_gen_id.side_effect = ["type-1", "type-2", "type-3", "type-4"]
        mock_db.query.return_value.filter.return_value.all.return_value = []

        def mock_item_type(**kwargs):
            mock_item = MagicMock()
            mock_item.__dict__.update(kwargs)
            return mock_item

        mock_item_type_class.side_effect = mock_item_type

        result = ensure_default_item_types(mock_user_id, mock_db)

        icons = [t.icon for t in result]
        expected_icons = ["Lightbulb", "FileText", "CheckSquare", "Target"]
        assert icons == expected_icons

    @patch("app.services.knowledge_defaults.ItemType")
    @patch("app.services.knowledge_defaults.generate_id")
    def test_ensure_default_item_types_colors(
        self, mock_gen_id, mock_item_type_class, mock_db, mock_user_id
    ):
        """Test that default item types have correct colors."""
        mock_gen_id.side_effect = ["type-1", "type-2", "type-3", "type-4"]
        mock_db.query.return_value.filter.return_value.all.return_value = []

        def mock_item_type(**kwargs):
            mock_item = MagicMock()
            mock_item.__dict__.update(kwargs)
            return mock_item

        mock_item_type_class.side_effect = mock_item_type

        result = ensure_default_item_types(mock_user_id, mock_db)

        colors = [t.color for t in result]
        expected_colors = [
            "text-yellow-500",
            "text-blue-500",
            "text-green-500",
            "text-purple-500",
        ]
        assert colors == expected_colors

    @patch("app.services.knowledge_defaults.ItemType")
    @patch("app.services.knowledge_defaults.generate_id")
    def test_ensure_default_item_types_transaction_rollback_on_error(
        self, mock_gen_id, mock_item_type_class, mock_db, mock_user_id
    ):
        """Test that database transaction rolls back on error."""
        mock_gen_id.side_effect = ["type-1", "type-2", "type-3", "type-4"]
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_db.commit.side_effect = Exception("Database error")

        def mock_item_type(**kwargs):
            mock_item = MagicMock()
            mock_item.__dict__.update(kwargs)
            return mock_item

        mock_item_type_class.side_effect = mock_item_type

        with pytest.raises(Exception, match="Database error"):
            ensure_default_item_types(mock_user_id, mock_db)
