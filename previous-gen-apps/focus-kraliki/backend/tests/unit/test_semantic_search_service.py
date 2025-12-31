"""
Comprehensive tests for Semantic Search Service to improve coverage
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.semantic_search import (
    SemanticSearchService,
    get_semantic_search_service,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
)
from app.models.user import User


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = MagicMock(spec=Session)
    db.query = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    return db


@pytest.fixture
def mock_user():
    """Mock user"""
    user = MagicMock(spec=User)
    user.id = "user123"
    return user


class TestSemanticSearchServiceInit:
    """Test service initialization"""

    def test_init_basic(self, mock_db, mock_user):
        """Test basic service initialization"""
        service = SemanticSearchService(mock_db, mock_user)
        assert service.db == mock_db
        assert service.user == mock_user
        assert service._client is None

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"})
    def test_client_property_lazy_init(self, mock_db, mock_user):
        """Test lazy initialization of OpenAI client"""
        with patch("app.services.semantic_search.OpenAI") as mock_openai:
            service = SemanticSearchService(mock_db, mock_user)
            client = service.client
            assert client is not None
            mock_openai.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    def test_client_property_no_api_key(self, mock_db, mock_user):
        """Test client property when no API key"""
        service = SemanticSearchService(mock_db, mock_user)
        client = service.client
        assert client is None


class TestComputeContentHash:
    """Test content hash computation"""

    def test_compute_content_hash_basic(self, mock_db, mock_user):
        """Test basic content hash computation"""
        service = SemanticSearchService(mock_db, mock_user)
        content = "Test content for hashing"
        hash_value = service._compute_content_hash(content)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 produces 64 hex chars

    def test_compute_content_hash_different_content(self, mock_db, mock_user):
        """Test that different content produces different hashes"""
        service = SemanticSearchService(mock_db, mock_user)
        hash1 = service._compute_content_hash("content1")
        hash2 = service._compute_content_hash("content2")
        assert hash1 != hash2

    def test_compute_content_hash_same_content(self, mock_db, mock_user):
        """Test that same content produces same hash"""
        service = SemanticSearchService(mock_db, mock_user)
        hash1 = service._compute_content_hash("same content")
        hash2 = service._compute_content_hash("same content")
        assert hash1 == hash2


class TestCosineSimilarity:
    """Test cosine similarity calculation"""

    def test_cosine_similarity_basic(self, mock_db, mock_user):
        """Test basic cosine similarity"""
        service = SemanticSearchService(mock_db, mock_user)
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        similarity = service._cosine_similarity(vec1, vec2)
        assert similarity == 1.0  # Perfect match

    def test_cosine_similarity_orthogonal(self, mock_db, mock_user):
        """Test cosine similarity for orthogonal vectors"""
        service = SemanticSearchService(mock_db, mock_user)
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]

        similarity = service._cosine_similarity(vec1, vec2)
        assert similarity == 0.0  # Orthogonal

    def test_cosine_similarity_empty_vectors(self, mock_db, mock_user):
        """Test cosine similarity with empty vectors"""
        service = SemanticSearchService(mock_db, mock_user)
        similarity = service._cosine_similarity([], [1.0, 2.0])
        assert similarity == 0.0

    def test_cosine_similarity_zero_norm(self, mock_db, mock_user):
        """Test cosine similarity with zero norm vectors"""
        service = SemanticSearchService(mock_db, mock_user)
        similarity = service._cosine_similarity([0.0, 0.0], [1.0, 1.0])
        assert similarity == 0.0


class TestBuildContent:
    """Test content building for different entity types"""

    def test_build_content_task(self, mock_db, mock_user):
        """Test building content for task entity"""
        service = SemanticSearchService(mock_db, mock_user)

        mock_entity = MagicMock()
        mock_entity.title = "Test Task"
        mock_entity.description = "Task description"
        mock_entity.status.value = "completed"
        mock_entity.priority = 1
        mock_entity.tags = ["urgent"]
        mock_entity.projectId = "proj1"
        mock_entity.dueDate = None

        content, metadata = service._build_content("task", mock_entity)

        assert "Test Task" in content
        assert metadata["status"] == "completed"
        assert metadata["priority"] == 1
        assert metadata["tags"] == ["urgent"]

    def test_build_content_project(self, mock_db, mock_user):
        """Test building content for project entity"""
        service = SemanticSearchService(mock_db, mock_user)

        mock_entity = MagicMock()
        mock_entity.name = "Project Name"
        mock_entity.description = "Project description"
        mock_entity.color = "#FF0000"
        mock_entity.icon = "folder"

        content, metadata = service._build_content("project", mock_entity)

        assert "Project Name" in content
        assert metadata["color"] == "#FF0000"
        assert metadata["icon"] == "folder"

    def test_build_content_knowledge_item(self, mock_db, mock_user):
        """Test building content for knowledge item entity"""
        service = SemanticSearchService(mock_db, mock_user)

        mock_entity = MagicMock()
        mock_entity.title = "Knowledge Title"
        mock_entity.content = "Knowledge content"
        mock_entity.typeId = "type1"
        mock_entity.completed = True
        mock_entity.item_metadata = {"key": "value"}

        content, metadata = service._build_content("knowledge_item", mock_entity)

        assert "Knowledge Title" in content
        assert metadata["typeId"] == "type1"
        assert metadata["completed"] is True

    def test_build_content_unknown_type(self, mock_db, mock_user):
        """Test building content for unknown entity type"""
        service = SemanticSearchService(mock_db, mock_user)

        content, metadata = service._build_content("unknown", MagicMock())

        assert isinstance(content, str)
        assert metadata == {}


class TestDeleteIndex:
    """Test index deletion"""

    def test_delete_index_success(self, mock_db, mock_user):
        """Test successful index deletion"""
        service = SemanticSearchService(mock_db, mock_user)
        mock_query = MagicMock()
        mock_query.filter.return_value.delete.return_value = 1
        mock_db.query.return_value = mock_query

        result = service.delete_index("task", "task123")

        assert result is True
        mock_db.commit.assert_called_once()

    def test_delete_index_no_match(self, mock_db, mock_user):
        """Test deletion when no index exists"""
        service = SemanticSearchService(mock_db, mock_user)
        mock_query = MagicMock()
        mock_query.filter.return_value.delete.return_value = 0
        mock_db.query.return_value = mock_query

        result = service.delete_index("task", "nonexistent")

        assert result is False


class TestGetIndexStats:
    """Test getting index statistics"""

    def test_get_index_stats(self, mock_db, mock_user):
        """Test getting index statistics"""
        service = SemanticSearchService(mock_db, mock_user)

        # Mock counts
        mock_query = MagicMock()
        mock_query.filter.return_value.count.side_effect = [10, 5, 3, 2, 2, 1]
        mock_db.query.return_value = mock_query

        stats = service.get_index_stats()

        assert stats["total"] == 10
        assert stats["withEmbeddings"] == 5
        assert "byType" in stats
        assert stats["embeddingModel"] == EMBEDDING_MODEL
        assert stats["embeddingDimensions"] == EMBEDDING_DIMENSIONS


class TestGetSemanticSearchService:
    """Test factory function"""

    def test_get_semantic_search_service(self, mock_db, mock_user):
        """Test factory function"""
        service = get_semantic_search_service(mock_db, mock_user)
        assert isinstance(service, SemanticSearchService)
        assert service.db == mock_db
        assert service.user == mock_user


class TestConstants:
    """Test module constants"""

    def test_embedding_model_constant(self):
        """Test embedding model constant"""
        assert EMBEDDING_MODEL == "voyage-3-lite"

    def test_embedding_dimensions_constant(self):
        """Test embedding dimensions constant"""
        assert EMBEDDING_DIMENSIONS == 512
