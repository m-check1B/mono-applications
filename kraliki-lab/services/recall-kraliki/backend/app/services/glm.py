"""
GLM 4.6 API Service
Handles semantic search, categorization, and pattern detection
"""

import logging
import os
from typing import List, Dict, Any, Optional, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from zhipuai import ZhipuAI

logger = logging.getLogger(__name__)


class GLMService:
    """GLM 4.6 API service for AI features"""

    def __init__(self):
        """Initialize GLM client"""
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("ZHIPUAI_API_KEY environment variable not set")

        from zhipuai import ZhipuAI

        self.client = ZhipuAI(api_key=api_key)
        self.fast_model = "glm-4-flash"  # Fast for embeddings
        self.advanced_model = "glm-4-plus"  # For complex analysis

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)
        """
        try:
            response = self.client.embeddings.create(
                model="embedding-2",  # GLM embedding model
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.exception("Embedding error")
            return []

    def categorize_content(self, content: str) -> Dict[str, Any]:
        """
        Auto-categorize content and suggest tags

        Args:
            content: Content to categorize

        Returns:
            Dict with category, tags, and confidence
        """
        try:
            prompt = f"""Analyze this content and categorize it.

Content:
{content}

Respond with JSON:
{{
  "category": "decision|insight|idea|learning|customer|competitor|research",
  "tags": ["tag1", "tag2", "tag3"],
  "confidence": 0.0-1.0,
  "summary": "one sentence summary"
}}
"""
            response = self.client.chat.completions.create(
                model=self.fast_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            import json

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.exception("Categorization error")
            return {"category": "unknown", "tags": [], "confidence": 0.0, "summary": ""}

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (-1 to 1, where 1 is identical)
        """
        try:
            if not vec1 or not vec2:
                return 0.0

            v1 = np.array(vec1)
            v2 = np.array(vec2)

            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.warning("Cosine similarity calculation error: %s", e)
            return 0.0

    def find_related_items(
        self, content: str, existing_items: List[Dict[str, Any]], top_k: int = 5
    ) -> List[str]:
        """
        Find related items using semantic similarity

        Args:
            content: New content
            existing_items: List of existing items with embeddings
            top_k: Number of related items to return

        Returns:
            List of related item IDs in format "category/id"
        """
        # Generate embedding for new content
        new_embedding = self.generate_embedding(content)
        if not new_embedding:
            return []

        # Calculate similarity with existing items
        similarities = []
        for item in existing_items:
            item_id = item.get("id")
            category = item.get("category")

            if not item_id or not category:
                continue

            # Get or generate embedding for existing item
            existing_embedding = item.get("embedding")
            if not existing_embedding:
                # Generate embedding from item content
                item_content = item.get("content", "")
                existing_embedding = self.generate_embedding(item_content)

                if not existing_embedding:
                    continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(new_embedding, existing_embedding)

            if similarity > 0:
                similarities.append(
                    {"id": f"{category}/{item_id}", "similarity": similarity}
                )

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        # Return top K item IDs
        return [item["id"] for item in similarities[:top_k]]

    def generate_wikilinks(self, content: str, item_id: str) -> List[str]:
        """
        Generate wikilink suggestions based on content

        Args:
            content: Content to analyze
            item_id: ID of current item

        Returns:
            List of suggested wikilinks
        """
        try:
            prompt = f"""Analyze this content and suggest wikilinks to related items.

Content:
{content}

Suggest 3-5 wikilinks in format: [[category/id|description]]

Examples:
- [[decisions/dec-2025-10-06-001|Use GLM 4.6 decision]]
- [[insights/ins-2025-10-06-002|Market research insight]]

Respond with JSON:
{{
  "wikilinks": ["[[category/id|description]]", ...]
}}
"""
            response = self.client.chat.completions.create(
                model=self.fast_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            import json

            result = json.loads(response.choices[0].message.content)
            return result.get("wikilinks", [])

        except Exception as e:
            logger.exception("Wikilink generation error")
            return []

    def detect_patterns(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect patterns across multiple items

        Args:
            items: List of items to analyze

        Returns:
            Dict with detected patterns and insights
        """
        try:
            # Create summary of items
            summaries = []
            for item in items[:20]:  # Limit to recent 20 items
                summaries.append(
                    f"- {item.get('title', 'Untitled')}: {item.get('content', '')[:200]}"
                )

            items_text = "\n".join(summaries)

            prompt = f"""Analyze these recent items and detect patterns:

Items:
{items_text}

Identify:
1. Recurring themes
2. Common challenges
3. Success patterns
4. Recommendations

Respond with JSON:
{{
  "patterns": [
    {{"theme": "...", "frequency": "...", "significance": "..."}}
  ],
  "insights": ["insight 1", "insight 2"],
  "recommendations": ["recommendation 1", "recommendation 2"]
}}
"""
            response = self.client.chat.completions.create(
                model=self.advanced_model,  # Use advanced model for analysis
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            import json

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.exception("Pattern detection error")
            return {"patterns": [], "insights": [], "recommendations": []}

    def chat(self, message: str, context: Optional[str] = None) -> str:
        """
        Chat with GLM about memory items

        Args:
            message: User message
            context: Optional context from search results

        Returns:
            AI response
        """
        try:
            messages = []

            if context:
                messages.append(
                    {"role": "system", "content": f"Context from memory:\n{context}"}
                )

            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=self.advanced_model, messages=messages
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.exception("Chat error")
            return f"Error: {str(e)}"


# Singleton instance
_glm_service = None


def get_glm_service() -> GLMService:
    """Get or create GLM service instance"""
    global _glm_service
    if _glm_service is None:
        _glm_service = GLMService()
    return _glm_service
