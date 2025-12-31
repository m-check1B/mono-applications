"""
Markdown Storage Service
Handles reading/writing markdown files with YAML frontmatter and wikilinks
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import frontmatter
import re

logger = logging.getLogger(__name__)

class StorageService:
    """Markdown storage service for recall-kraliki"""

    def __init__(self, memory_dir: Optional[str] = None):
        """
        Initialize storage service

        Args:
            memory_dir: Path to memory directory (defaults to ../memory)
        """
        if memory_dir is None:
            # Default to memory/ directory relative to backend/
            backend_dir = Path(__file__).parent.parent.parent
            memory_dir = backend_dir / "memory"

        self.memory_dir = Path(memory_dir)
        self.categories = [
            "decisions",
            "insights",
            "ideas",
            "learnings",
            "customers",
            "competitors",
            "research",
            "sessions",
            "agent-learnings",
            "system-events"
        ]

        # Ensure all category directories exist
        for category in self.categories:
            (self.memory_dir / category).mkdir(parents=True, exist_ok=True)

    def generate_id(self, category: str) -> str:
        """
        Generate unique ID for item

        Format: {category-prefix}-YYYY-MM-DD-NNN

        Args:
            category: Category name

        Returns:
            Generated ID
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        prefix = category[:3]  # First 3 letters
        id_prefix = f"{prefix}-{date_str}"

        # Find existing files with same prefix
        category_dir = self.memory_dir / category
        if not category_dir.exists():
            return f"{id_prefix}-001"

        existing = list(category_dir.glob(f"{id_prefix}-*.md"))
        if not existing:
            return f"{id_prefix}-001"

        # Find max number
        max_num = 0
        for filepath in existing:
            match = re.search(r'-(\d{3})(?:-|\.)', filepath.stem)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)

        return f"{id_prefix}-{(max_num + 1):03d}"

    def save_item(
        self,
        category: str,
        data: Dict[str, Any],
        content: str
    ) -> str:
        """
        Save item as markdown file with YAML frontmatter

        Args:
            category: Category (decisions, insights, etc.)
            data: Metadata dict
            content: Markdown content

        Returns:
            File path of saved item
        """
        # Generate ID if not provided
        if "id" not in data:
            data["id"] = self.generate_id(category)

        # Add date if not provided
        if "date" not in data:
            data["date"] = datetime.now().strftime("%Y-%m-%d")

        # Create frontmatter post
        post = frontmatter.Post(content)
        post.metadata = data

        # Generate filename
        item_id = data["id"]
        title_slug = data.get("title", "untitled").lower()
        title_slug = re.sub(r'[^a-z0-9]+', '-', title_slug)[:50]
        filename = f"{item_id}-{title_slug}.md"

        # Save file
        category_dir = self.memory_dir / category
        filepath = category_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

        return str(filepath)

    def load_item(self, category: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Load item by ID

        Args:
            category: Category name
            item_id: Item ID

        Returns:
            Dict with metadata and content, or None if not found
        """
        category_dir = self.memory_dir / category
        if not category_dir.exists():
            return None

        # Find file with matching ID
        files = list(category_dir.glob(f"{item_id}-*.md"))
        if not files:
            return None

        filepath = files[0]
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        return {
            **post.metadata,
            "content": post.content,
            "file_path": str(filepath)
        }

    def list_items(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List items from category

        Args:
            category: Category to list (or all if None)
            limit: Max items to return
            offset: Number of items to skip

        Returns:
            List of items with metadata and content
        """
        items = []

        categories = [category] if category else self.categories

        for cat in categories:
            cat_dir = self.memory_dir / cat
            if not cat_dir.exists():
                continue

            for filepath in cat_dir.glob("*.md"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)

                    items.append({
                        **post.metadata,
                        "content": post.content,
                        "file_path": str(filepath),
                        "category": cat
                    })
                except Exception as e:
                    logger.warning("Error loading %s: %s", filepath, e)
                    continue

        # Sort all items by date (newest first)
        # Handle both datetime.date objects and strings
        def get_sortable_date(x):
            date_val = x.get("date", "")
            if hasattr(date_val, 'isoformat'):
                return date_val.isoformat()
            return str(date_val) if date_val else ""
        items.sort(key=get_sortable_date, reverse=True)

        # Apply offset and limit
        return items[offset:offset + limit]

    def search_items(
        self,
        query: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search items by keyword

        Args:
            query: Search query
            category: Optional category filter

        Returns:
            List of matching items
        """
        query_lower = query.lower()
        results = []

        for item in self.list_items(category=category):
            # Search in title, content, and tags
            title = item.get("title", "").lower()
            content = item.get("content", "").lower()
            tags = " ".join(item.get("tags", [])).lower()

            if (query_lower in title or
                query_lower in content or
                query_lower in tags):
                results.append(item)

        return results

    def extract_wikilinks(self, content: str) -> List[str]:
        """
        Extract wikilinks from markdown content

        Args:
            content: Markdown content

        Returns:
            List of wikilink targets (e.g., ["decisions/dec-2025-10-06-001", ...])
        """
        # Pattern: [[category/id]] or [[category/id|description]]
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(pattern, content)
        return matches

    def resolve_wikilink(self, wikilink: str) -> Optional[Dict[str, Any]]:
        """
        Resolve wikilink to actual item

        Args:
            wikilink: Wikilink target (e.g., "decisions/dec-2025-10-06-001")

        Returns:
            Item dict or None if not found
        """
        parts = wikilink.split('/')
        if len(parts) != 2:
            return None

        category, item_id = parts
        return self.load_item(category, item_id)

    def get_related_items(self, item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get items related via wikilinks

        Args:
            item: Item dict

        Returns:
            List of related items
        """
        content = item.get("content", "")
        wikilinks = self.extract_wikilinks(content)

        related = []
        for link in wikilinks:
            resolved = self.resolve_wikilink(link)
            if resolved:
                related.append(resolved)

        return related


# Singleton instance
_storage_service = None

def get_storage_service() -> StorageService:
    """Get or create storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
