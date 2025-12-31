"""
Test cosine similarity calculation in GLM service
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.glm import GLMService
from typing import Dict, Any


def test_cosine_similarity_basic():
    """Test basic cosine similarity calculation"""
    # Import the method directly to avoid initialization
    from app.services.glm import GLMService

    # Create a dummy instance without calling __init__
    glm = object.__new__(GLMService)

    # Test identical vectors
    vec1 = [1.0, 2.0, 3.0]
    vec2 = [1.0, 2.0, 3.0]
    similarity = glm._cosine_similarity(vec1, vec2)
    assert abs(similarity - 1.0) < 0.001, "Identical vectors should have similarity 1.0"

    # Test orthogonal vectors
    vec1 = [1.0, 0.0]
    vec2 = [0.0, 1.0]
    similarity = glm._cosine_similarity(vec1, vec2)
    assert abs(similarity - 0.0) < 0.001, (
        "Orthogonal vectors should have similarity 0.0"
    )

    # Test opposite vectors
    vec1 = [1.0, 1.0]
    vec2 = [-1.0, -1.0]
    similarity = glm._cosine_similarity(vec1, vec2)
    assert abs(similarity - (-1.0)) < 0.001, (
        "Opposite vectors should have similarity -1.0"
    )

    # Test empty vectors
    vec1 = []
    vec2 = [1.0, 2.0]
    similarity = glm._cosine_similarity(vec1, vec2)
    assert similarity == 0.0, "Empty vectors should return similarity 0.0"

    print("✓ All cosine similarity tests passed")


def test_find_related_items_structure():
    """Test find_related_items returns correct structure"""
    from app.services.glm import GLMService

    # Create a dummy instance without calling __init__
    glm = object.__new__(GLMService)

    # Create items with pre-generated embeddings for testing
    items_with_embeddings = [
        {
            "id": "test-001",
            "category": "test",
            "content": "AI machine learning deep learning",
            "embedding": [0.1, 0.2, 0.3],
        },
        {
            "id": "test-002",
            "category": "test",
            "content": "cooking recipes food",
            "embedding": [0.9, 0.8, 0.7],
        },
    ]

    # Test with similar content
    similar_content = "AI neural networks"

    # Mock the generate_embedding to return a known embedding
    original_generate = glm.generate_embedding
    glm.generate_embedding = (
        lambda text: [0.15, 0.25, 0.35] if text == similar_content else None
    )

    # This would normally make an API call, but we're mocking it
    # The structure test ensures the method returns the right format

    result = glm.find_related_items(
        content=similar_content, existing_items=items_with_embeddings, top_k=2
    )

    # Verify result is a list of strings in "category/id" format
    assert isinstance(result, list), "Result should be a list"

    for item_id in result:
        assert isinstance(item_id, str), "Item ID should be a string"
        assert "/" in item_id, "Item ID should be in 'category/id' format"
        parts = item_id.split("/")
        assert len(parts) == 2, "Item ID should have exactly 2 parts when split by '/'"

    # Restore original method
    glm.generate_embedding = original_generate

    print("✓ find_related_items structure test passed")


def test_find_related_items_sorting():
    """Test that find_related_items sorts by similarity"""
    from app.services.glm import GLMService

    # Create a dummy instance without calling __init__
    glm = object.__new__(GLMService)

    # Create items with varying similarity
    items = [
        {"id": "low-sim", "category": "test", "embedding": [0.9, 0.8, 0.7]},
        {"id": "high-sim", "category": "test", "embedding": [0.5, 0.6, 0.7]},
        {"id": "med-sim", "category": "test", "embedding": [0.7, 0.7, 0.7]},
    ]

    # Query embedding
    query_embedding = [0.5, 0.6, 0.7]
    glm.generate_embedding = lambda text: query_embedding

    result = glm.find_related_items(content="test query", existing_items=items, top_k=3)

    # High similarity should be first
    assert "test/high-sim" in result[0], "Highest similarity item should be first"

    print("✓ find_related_items sorting test passed")


if __name__ == "__main__":
    test_cosine_similarity_basic()
    test_find_related_items_structure()
    test_find_related_items_sorting()
    print("\n✅ All tests passed!")
