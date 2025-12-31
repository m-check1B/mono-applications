#!/usr/bin/env python3
"""
recall-kraliki MCP Server
Provides Claude Code integration via Model Context Protocol
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Import recall-kraliki services
from app.services.storage import StorageService
from app.services.glm import GLMService

# Initialize FastMCP server
mcp = FastMCP("recall-kraliki")

# Initialize services
storage = StorageService()
glm = GLMService()


@mcp.tool()
async def recall_search(
    query: str,
    category: Optional[str] = None,
    search_type: str = "hybrid",
    limit: int = 10
) -> str:
    """
    Search recall-kraliki knowledge base using hybrid search (keyword + semantic).

    Use this to find relevant decisions, insights, learnings, and other captured knowledge.

    Args:
        query: Search query (natural language or keywords)
        category: Filter by category (decisions, insights, ideas, learnings, customers, competitors, research, sessions)
        search_type: "hybrid" (default), "keyword", or "semantic"
        limit: Maximum results to return (default: 10)

    Returns:
        Formatted search results with content snippets

    Examples:
        - recall_search("pricing strategy")
        - recall_search("GLM 4.6 decision", category="decisions")
        - recall_search("avatar market research", search_type="semantic")
    """
    try:
        if search_type == "keyword":
            # Keyword search
            results = storage.search_items(query=query, category=category)
            results = results[:limit]

        elif search_type == "semantic":
            # Semantic search
            all_items = storage.list_items(category=category, limit=1000)
            similar_ids = glm.find_related_items(query, all_items)

            results = []
            for item_id in similar_ids[:limit]:
                if "/" in item_id:
                    cat, id_only = item_id.split("/", 1)
                    item = storage.load_item(cat, id_only)
                    if item:
                        results.append(item)

        else:  # hybrid
            # Keyword search
            keyword_results = storage.search_items(query=query, category=category)

            # Semantic search
            all_items = storage.list_items(category=category, limit=1000)
            semantic_ids = glm.find_related_items(query, all_items)

            # Combine results
            seen_ids = set()
            results = []

            for r in keyword_results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    results.append(r)

            for item_id in semantic_ids:
                if "/" in item_id:
                    cat, id_only = item_id.split("/", 1)
                    full_id = f"{cat}/{id_only}"
                    if full_id not in seen_ids:
                        item = storage.load_item(cat, id_only)
                        if item:
                            seen_ids.add(full_id)
                            results.append(item)

            results = results[:limit]

        # Format results
        if not results:
            return f"No results found for query: {query}"

        output = [f"Found {len(results)} results for '{query}':\n"]

        for i, item in enumerate(results, 1):
            title = item.get("title", item["id"])
            category_name = item["category"]
            tags = ", ".join(item.get("tags", []))
            content = item["content"][:200] + "..." if len(item["content"]) > 200 else item["content"]

            output.append(f"\n{i}. [{category_name}] {title}")
            if tags:
                output.append(f"   Tags: {tags}")
            output.append(f"   {content}")
            output.append(f"   File: {item['file_path']}")

        return "\n".join(output)

    except Exception as e:
        return f"Error searching recall: {str(e)}"


@mcp.tool()
async def recall_capture(
    content: str,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    auto_categorize: bool = True
) -> str:
    """
    Capture new knowledge item to recall-kraliki.

    Use this to save important decisions, insights, learnings for future recall.

    Args:
        content: The content to capture (markdown format)
        category: Category (decisions, insights, ideas, learnings, customers, competitors, research, sessions)
        tags: Comma-separated tags (e.g., "ai,infrastructure,pricing")
        auto_categorize: Auto-categorize using GLM 4.6 if category not provided (default: True)

    Returns:
        Confirmation with item ID and file path

    Examples:
        - recall_capture("Decision: Use GLM 4.6 for AI features", category="decisions", tags="ai,architecture")
        - recall_capture("Avatar market growing to $117B by 2034", category="research")
    """
    try:
        # Parse tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else []

        # Auto-categorize if needed
        if not category and auto_categorize:
            categorization = glm.categorize_content(content)
            category = categorization["category"]
            suggested_tags = categorization["tags"]
            tag_list.extend(suggested_tags)
            tag_list = list(set(tag_list))  # Deduplicate
        else:
            category = category or "general"

        # Get existing items for auto-linking
        existing_items = []
        all_categories = ["decisions", "insights", "ideas", "learnings",
                        "customers", "competitors", "research", "sessions"]
        for cat in all_categories:
            existing_items.extend(storage.list_items(category=cat, limit=100))

        # Find related items
        related_item_ids = glm.find_related_items(content, existing_items)

        # Generate item ID
        item_id = storage.generate_id(category)

        # Generate wikilinks
        wikilinks = glm.generate_wikilinks(content, item_id)

        # Prepare metadata
        metadata = {
            "tags": tag_list,
            "related": related_item_ids,
            "wikilinks": wikilinks
        }

        # Save item
        file_path = storage.save_item(
            category=category,
            data=metadata,
            content=content
        )

        return (
            f"✓ Captured to recall-kraliki:\n"
            f"  ID: {item_id}\n"
            f"  Category: {category}\n"
            f"  Tags: {', '.join(tag_list)}\n"
            f"  Related items: {len(related_item_ids)}\n"
            f"  File: {file_path}"
        )

    except Exception as e:
        return f"Error capturing to recall: {str(e)}"


@mcp.tool()
async def recall_get(category: str, item_id: str) -> str:
    """
    Get full content of a specific recall item.

    Args:
        category: Item category
        item_id: Item ID (e.g., "dec-2025-10-06-001")

    Returns:
        Full item content with metadata

    Example:
        - recall_get("decisions", "dec-2025-10-06-001")
    """
    try:
        item = storage.load_item(category, item_id)
        if not item:
            return f"Item not found: {category}/{item_id}"

        title = item.get("title", item_id)
        tags = ", ".join(item.get("tags", []))
        content = item["content"]

        output = [
            f"[{category}] {title}",
            f"Tags: {tags}" if tags else "",
            f"File: {item['file_path']}",
            "",
            content
        ]

        return "\n".join(output)

    except Exception as e:
        return f"Error getting item: {str(e)}"


@mcp.tool()
async def recall_recent(category: Optional[str] = None, limit: int = 10) -> str:
    """
    Get recent recall items.

    Args:
        category: Filter by category (optional)
        limit: Maximum items to return (default: 10)

    Returns:
        List of recent items with snippets

    Examples:
        - recall_recent()
        - recall_recent(category="decisions", limit=5)
    """
    try:
        items = storage.list_items(category=category, limit=limit)

        if not items:
            return "No items found"

        output = [f"Recent {category or 'all'} items ({len(items)}):\n"]

        for i, item in enumerate(items, 1):
            title = item.get("title", item["id"])
            category_name = item["category"]
            content = item["content"][:150] + "..." if len(item["content"]) > 150 else item["content"]

            output.append(f"\n{i}. [{category_name}] {title}")
            output.append(f"   {content}")

        return "\n".join(output)

    except Exception as e:
        return f"Error getting recent items: {str(e)}"


@mcp.tool()
async def recall_patterns(category: Optional[str] = None, limit: int = 100) -> str:
    """
    Detect patterns across recall items using AI analysis.

    Identifies recurring themes, clusters of related content, and suggests new connections.

    Args:
        category: Filter by category (optional)
        limit: Maximum items to analyze (default: 100)

    Returns:
        Pattern analysis with themes, clusters, and suggestions

    Example:
        - recall_patterns()
        - recall_patterns(category="decisions")
    """
    try:
        items = storage.list_items(category=category, limit=limit)

        if not items:
            return "No items to analyze"

        patterns = glm.detect_patterns(items)

        output = [f"Pattern Analysis ({len(items)} items):\n"]

        if "themes" in patterns:
            output.append("Recurring Themes:")
            for theme in patterns["themes"]:
                output.append(f"  • {theme}")

        if "clusters" in patterns:
            output.append("\nContent Clusters:")
            for cluster in patterns["clusters"]:
                output.append(f"  • {cluster}")

        if "suggestions" in patterns:
            output.append("\nSuggested Connections:")
            for suggestion in patterns["suggestions"]:
                output.append(f"  • {suggestion}")

        return "\n".join(output)

    except Exception as e:
        return f"Error analyzing patterns: {str(e)}"


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
