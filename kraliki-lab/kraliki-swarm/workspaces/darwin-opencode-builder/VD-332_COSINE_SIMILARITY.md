# VD-332: Implement cosine similarity calculation in GLM service

## Issue
[VD-332] [Recall-Kraliki] Implement cosine similarity calculation in GLM service

## Changes Made

### File: `/home/adminmatej/github/applications/recall-kraliki/backend/app/services/glm.py`

1. **Added numpy import**
   - Added `import numpy as np` to support vector operations

2. **Added `_cosine_similarity` method**
   - Private helper method to calculate cosine similarity between two vectors
   - Handles edge cases: zero-length vectors, empty vectors
   - Returns similarity score between -1 and 1 (1 = identical)

3. **Updated `find_related_items` method**
   - Removed TODO comment
   - Implemented full cosine similarity calculation
   - Generates embeddings for items without pre-computed embeddings
   - Sorts results by similarity (highest first)
   - Returns top K item IDs in "category/id" format

## Implementation Details

The cosine similarity calculation uses numpy for efficient vector operations:

```python
cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)
```

Where:
- A · B is the dot product
- ||A|| is the L2 norm (magnitude)

Key features:
- Handles missing embeddings by generating them on-the-fly from item content
- Filters out items with zero similarity
- Sorts results by similarity score (descending)
- Returns results in wikilink format ("category/id")

## Testing

Created `/home/adminmatej/github/applications/recall-kraliki/backend/test_cosine_similarity.py`

Test coverage:
1. **Cosine similarity basics**
   - Identical vectors → similarity = 1.0
   - Orthogonal vectors → similarity = 0.0
   - Opposite vectors → similarity = -1.0
   - Empty vectors → similarity = 0.0

2. **find_related_items structure**
   - Returns list of strings
   - IDs in correct format "category/id"
   - Handles items with pre-computed embeddings

3. **find_related_items sorting**
   - Results sorted by similarity (highest first)

All tests passing ✅

## Verification

Verification script passed:
- tests: OK
- build: OK
- typecheck: OK
- lint: OK

## Impact

This feature enables semantic search in recall-kraliki:
- Users can find related items by semantic similarity
- Hybrid search (keyword + semantic) now fully functional
- Auto-linking between related items now works
- Knowledge graph can surface related content

## Dependencies

- numpy (already in requirements.txt)
- zhipuai (already in requirements.txt)

## Points Earned

150 points for completing VD-332
