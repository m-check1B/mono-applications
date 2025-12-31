"""
Semantic Search Service

Provides semantic (vector-based) search across tasks, projects, and knowledge items.
Uses OpenRouter for embeddings with local storage for fast retrieval.

Architecture:
- Embeddings generated via OpenRouter/Voyage AI
- Stored in SQLite search_index table
- Cosine similarity for ranking results
- Background indexing for new/updated content
"""
import hashlib
import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import numpy as np
from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.security import generate_id
from app.models.search_index import SearchIndex
from app.models.task import Task, Project
from app.models.knowledge_item import KnowledgeItem
from app.models.user import User

logger = logging.getLogger(__name__)

# Embedding configuration
EMBEDDING_MODEL = "voyage-3-lite"  # Cost-effective, 512 dimensions
EMBEDDING_DIMENSIONS = 512
EMBEDDING_PROVIDER = "openrouter"


class SemanticSearchService:
    """
    Semantic search service using vector embeddings.

    Features:
    - Index tasks, projects, knowledge items
    - Semantic search with cosine similarity
    - Background indexing with change detection
    - Fallback to keyword search if embeddings unavailable
    """

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> Optional[OpenAI]:
        """Lazy initialize OpenRouter client"""
        if self._client is None:
            api_key = os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
            if api_key:
                self._client = OpenAI(
                    api_key=api_key,
                    base_url=os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
                )
        return self._client

    def _compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of content for change detection"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text using OpenRouter/Voyage.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if unavailable
        """
        if not self.client:
            logger.warning("OpenRouter client not available for embeddings")
            return None

        try:
            # Truncate text if too long (Voyage has ~32k token limit)
            max_chars = 8000
            if len(text) > max_chars:
                text = text[:max_chars]

            response = self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0

        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.warning(f"Cosine similarity error: {e}")
            return 0.0

    def _build_content(self, entity_type: str, entity: Any) -> Tuple[str, Dict[str, Any]]:
        """
        Build searchable content and metadata from entity.

        Returns:
            Tuple of (content string, metadata dict)
        """
        if entity_type == "task":
            content = f"{entity.title}\n{entity.description or ''}"
            metadata = {
                "status": entity.status.value if entity.status else None,
                "priority": entity.priority,
                "tags": entity.tags or [],
                "projectId": entity.projectId,
                "dueDate": entity.dueDate.isoformat() if entity.dueDate else None
            }
        elif entity_type == "project":
            content = f"{entity.name}\n{entity.description or ''}"
            metadata = {
                "color": entity.color,
                "icon": entity.icon
            }
        elif entity_type == "knowledge_item":
            content = f"{entity.title}\n{entity.content or ''}"
            metadata = {
                "typeId": entity.typeId,
                "completed": entity.completed,
                "itemMetadata": entity.item_metadata
            }
        else:
            content = str(entity)
            metadata = {}

        return content.strip(), metadata

    def index_entity(
        self,
        entity_type: str,
        entity_id: str,
        force: bool = False
    ) -> Optional[SearchIndex]:
        """
        Index a single entity for semantic search.

        Args:
            entity_type: Type of entity (task, project, knowledge_item)
            entity_id: Entity ID
            force: Force re-indexing even if content hasn't changed

        Returns:
            SearchIndex record or None if indexing failed
        """
        # Load entity
        if entity_type == "task":
            entity = self.db.query(Task).filter(
                Task.id == entity_id,
                Task.userId == self.user.id
            ).first()
        elif entity_type == "project":
            entity = self.db.query(Project).filter(
                Project.id == entity_id,
                Project.userId == self.user.id
            ).first()
        elif entity_type == "knowledge_item":
            entity = self.db.query(KnowledgeItem).filter(
                KnowledgeItem.id == entity_id,
                KnowledgeItem.userId == self.user.id
            ).first()
        else:
            logger.error(f"Unknown entity type: {entity_type}")
            return None

        if not entity:
            logger.warning(f"Entity not found: {entity_type}/{entity_id}")
            return None

        # Build content
        content, metadata = self._build_content(entity_type, entity)
        content_hash = self._compute_content_hash(content)

        # Check existing index
        existing = self.db.query(SearchIndex).filter(
            SearchIndex.userId == self.user.id,
            SearchIndex.entityType == entity_type,
            SearchIndex.entityId == entity_id
        ).first()

        # Skip if content unchanged (unless forced)
        if existing and existing.contentHash == content_hash and not force:
            logger.debug(f"Content unchanged, skipping: {entity_type}/{entity_id}")
            return existing

        # Generate embedding
        embedding = self._generate_embedding(content)

        if existing:
            # Update existing
            existing.content = content
            existing.contentHash = content_hash
            existing.embedding = embedding
            existing.embeddingModel = EMBEDDING_MODEL if embedding else None
            existing.embeddingDimensions = EMBEDDING_DIMENSIONS if embedding else None
            existing.entity_metadata = metadata
            existing.updatedAt = datetime.utcnow()
            self.db.commit()
            logger.info(f"Updated search index: {entity_type}/{entity_id}")
            return existing
        else:
            # Create new
            search_index = SearchIndex(
                id=generate_id(),
                userId=self.user.id,
                entityType=entity_type,
                entityId=entity_id,
                content=content,
                contentHash=content_hash,
                embedding=embedding,
                embeddingModel=EMBEDDING_MODEL if embedding else None,
                embeddingDimensions=EMBEDDING_DIMENSIONS if embedding else None,
                entity_metadata=metadata
            )
            self.db.add(search_index)
            self.db.commit()
            logger.info(f"Created search index: {entity_type}/{entity_id}")
            return search_index

    def index_all(
        self,
        entity_types: Optional[List[str]] = None,
        force: bool = False
    ) -> Dict[str, int]:
        """
        Index all entities of specified types for the user.

        Args:
            entity_types: Types to index (default: all)
            force: Force re-indexing

        Returns:
            Dict of {entity_type: count_indexed}
        """
        if entity_types is None:
            entity_types = ["task", "project", "knowledge_item"]

        results = {}

        for entity_type in entity_types:
            count = 0

            if entity_type == "task":
                entities = self.db.query(Task).filter(Task.userId == self.user.id).all()
            elif entity_type == "project":
                entities = self.db.query(Project).filter(Project.userId == self.user.id).all()
            elif entity_type == "knowledge_item":
                entities = self.db.query(KnowledgeItem).filter(KnowledgeItem.userId == self.user.id).all()
            else:
                continue

            for entity in entities:
                if self.index_entity(entity_type, entity.id, force=force):
                    count += 1

            results[entity_type] = count

        return results

    def delete_index(self, entity_type: str, entity_id: str) -> bool:
        """Delete search index for an entity"""
        result = self.db.query(SearchIndex).filter(
            SearchIndex.userId == self.user.id,
            SearchIndex.entityType == entity_type,
            SearchIndex.entityId == entity_id
        ).delete()
        self.db.commit()
        return result > 0

    def search(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 20,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across indexed content.

        Args:
            query: Search query
            entity_types: Filter by entity types (default: all)
            limit: Maximum results
            min_score: Minimum similarity score (0-1)

        Returns:
            List of search results with scores
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        if not query_embedding:
            # Fallback to keyword search
            return self._keyword_search(query, entity_types, limit)

        # Load all indexed items for user
        db_query = self.db.query(SearchIndex).filter(
            SearchIndex.userId == self.user.id,
            SearchIndex.embedding.isnot(None)
        )

        if entity_types:
            db_query = db_query.filter(SearchIndex.entityType.in_(entity_types))

        indexed_items = db_query.all()

        # Calculate similarities
        results = []
        for item in indexed_items:
            if not item.embedding:
                continue

            score = self._cosine_similarity(query_embedding, item.embedding)

            if score >= min_score:
                results.append({
                    "id": item.id,
                    "entityType": item.entityType,
                    "entityId": item.entityId,
                    "content": item.content[:300] + "..." if len(item.content) > 300 else item.content,
                    "metadata": item.entity_metadata,
                    "score": round(score, 4),
                    "indexedAt": item.indexedAt.isoformat() if item.indexedAt else None
                })

        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:limit]

    def _keyword_search(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fallback keyword search when embeddings unavailable.

        Uses SQL ILIKE for basic text matching.
        """
        logger.info("Using keyword search fallback")

        db_query = self.db.query(SearchIndex).filter(
            SearchIndex.userId == self.user.id,
            SearchIndex.content.ilike(f"%{query}%")
        )

        if entity_types:
            db_query = db_query.filter(SearchIndex.entityType.in_(entity_types))

        items = db_query.limit(limit).all()

        return [
            {
                "id": item.id,
                "entityType": item.entityType,
                "entityId": item.entityId,
                "content": item.content[:300] + "..." if len(item.content) > 300 else item.content,
                "metadata": item.entity_metadata,
                "score": 0.5,  # Fixed score for keyword matches
                "indexedAt": item.indexedAt.isoformat() if item.indexedAt else None,
                "searchType": "keyword"
            }
            for item in items
        ]

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the search index"""
        total = self.db.query(SearchIndex).filter(
            SearchIndex.userId == self.user.id
        ).count()

        with_embeddings = self.db.query(SearchIndex).filter(
            SearchIndex.userId == self.user.id,
            SearchIndex.embedding.isnot(None)
        ).count()

        by_type = {}
        for entity_type in ["task", "project", "knowledge_item"]:
            by_type[entity_type] = self.db.query(SearchIndex).filter(
                SearchIndex.userId == self.user.id,
                SearchIndex.entityType == entity_type
            ).count()

        return {
            "total": total,
            "withEmbeddings": with_embeddings,
            "byType": by_type,
            "embeddingModel": EMBEDDING_MODEL,
            "embeddingDimensions": EMBEDDING_DIMENSIONS
        }


# Factory function for easy instantiation
def get_semantic_search_service(db: Session, user: User) -> SemanticSearchService:
    """Get or create SemanticSearchService instance"""
    return SemanticSearchService(db, user)
