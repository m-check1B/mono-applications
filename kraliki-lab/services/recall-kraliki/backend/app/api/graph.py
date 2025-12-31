"""Graph API routes - knowledge graph visualization"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.storage import StorageService
from ..services.glm import GLMService

router = APIRouter(prefix="/graph", tags=["graph"])
storage = StorageService()
glm = GLMService()


class Node(BaseModel):
    """Graph node"""
    id: str
    label: str
    category: str
    tags: List[str]
    size: int = 1  # Based on connections


class Edge(BaseModel):
    """Graph edge"""
    source: str
    target: str
    type: str  # "wikilink", "related", "tag"


class GraphResponse(BaseModel):
    """Graph visualization data"""
    nodes: List[Node]
    edges: List[Edge]
    stats: Dict[str, Any]


@router.get("/", response_model=GraphResponse)
async def get_graph(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    depth: int = 2,
    limit: int = 100
):
    """
    Get knowledge graph data

    - Nodes: memory items
    - Edges: wikilinks, related items, shared tags
    - Filter by category or tag
    - Control depth and size
    """
    try:
        # Get items
        items = storage.list_items(category=category, limit=limit)

        # Filter by tag if provided
        if tag:
            items = [item for item in items if tag in item.get("tags", [])]

        # Build nodes
        nodes = []
        node_connections = {}  # Count connections for sizing

        for item in items:
            item_id = f"{item['category']}/{item['id']}"
            node_connections[item_id] = 0

            nodes.append(Node(
                id=item_id,
                label=item.get("title", item["id"]),
                category=item["category"],
                tags=item.get("tags", []),
                size=1  # Will update after counting connections
            ))

        # Build edges
        edges = []
        seen_edges = set()

        for item in items:
            item_id = f"{item['category']}/{item['id']}"

            # Wikilink edges
            wikilinks = item.get("wikilinks", [])
            for link in wikilinks:
                # Parse wikilink: [[category/id]] or [[category/id|description]]
                link_target = link.strip("[]").split("|")[0]
                edge_key = tuple(sorted([item_id, link_target]))

                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append(Edge(
                        source=item_id,
                        target=link_target,
                        type="wikilink"
                    ))
                    node_connections[item_id] = node_connections.get(item_id, 0) + 1
                    node_connections[link_target] = node_connections.get(link_target, 0) + 1

            # Related item edges
            related = item.get("related", [])
            for rel_id in related:
                edge_key = tuple(sorted([item_id, rel_id]))

                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append(Edge(
                        source=item_id,
                        target=rel_id,
                        type="related"
                    ))
                    node_connections[item_id] = node_connections.get(item_id, 0) + 1
                    node_connections[rel_id] = node_connections.get(rel_id, 0) + 1

        # Update node sizes based on connections
        for node in nodes:
            connections = node_connections.get(node.id, 0)
            node.size = max(1, min(10, connections))  # Size 1-10

        # Calculate stats
        stats = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "categories": len(set(n.category for n in nodes)),
            "avg_connections": sum(node_connections.values()) / len(nodes) if nodes else 0,
            "most_connected": max(node_connections.items(), key=lambda x: x[1])[0] if node_connections else None
        }

        return GraphResponse(
            nodes=nodes,
            edges=edges,
            stats=stats
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate graph: {str(e)}")


@router.get("/node/{category}/{item_id}")
async def get_node_details(category: str, item_id: str):
    """Get detailed information about a specific node"""
    item = storage.load_item(category, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Node not found")

    # Get connected nodes
    wikilinks = storage.extract_wikilinks(item["content"])
    connected_items = []

    for link in wikilinks:
        resolved = storage.resolve_wikilink(link)
        if resolved:
            connected_items.append({
                "id": f"{resolved['category']}/{resolved['id']}",
                "title": resolved.get("title", resolved["id"]),
                "category": resolved["category"]
            })

    return {
        "item": item,
        "connections": connected_items,
        "connection_count": len(connected_items)
    }


@router.get("/patterns")
async def detect_patterns(category: Optional[str] = None, limit: int = 100):
    """
    Detect patterns across memory items using GLM 4.6

    - Identifies recurring themes
    - Finds clusters of related content
    - Suggests new connections
    """
    try:
        items = storage.list_items(category=category, limit=limit)

        if not items:
            return {"patterns": [], "message": "No items found"}

        patterns = glm.detect_patterns(items)

        return patterns

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern detection failed: {str(e)}")
