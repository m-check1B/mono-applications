import logging
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from ..models.board import Board, BoardConfig
from ..models.post import Post, PostCreate

logger = logging.getLogger(__name__)

class BoardManager:
    """Manages boards and posts"""

    def __init__(self, boards_path: str = "./boards"):
        self.boards_path = Path(boards_path)
        self.config_path = self.boards_path / "boards.yaml"
        self.boards_config = self._load_boards_config()

    def _load_boards_config(self) -> Dict[str, BoardConfig]:
        """Load boards configuration from YAML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Boards config not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)

        return {
            board_id: BoardConfig(**config)
            for board_id, config in data['boards'].items()
        }

    def get_boards(self) -> List[Board]:
        """Get all boards with stats"""
        boards = []
        for board_id, config in self.boards_config.items():
            board_path = self.boards_path / board_id / "posts"
            board_path.mkdir(parents=True, exist_ok=True)

            # Count posts
            post_count = len(list(board_path.glob("*.md")))

            boards.append(Board(
                id=board_id,
                name=config.name,
                description=config.description,
                icon=config.icon,
                color=config.color,
                post_count=post_count,
                agent_count=len(config.allowed_agents)
            ))

        return boards

    def get_board(self, board_id: str) -> Optional[Board]:
        """Get a specific board"""
        if board_id not in self.boards_config:
            return None

        boards = self.get_boards()
        return next((b for b in boards if b.id == board_id), None)

    def create_post(self, board_id: str, post_data: PostCreate) -> Post:
        """Create a new post on a board"""
        if board_id not in self.boards_config:
            raise ValueError(f"Board not found: {board_id}")

        # Generate post ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        post_id = f"{board_id}-{post_data.content_type}-{timestamp}-{post_data.agent_type}"

        # Create post directory (updates or journal)
        post_dir = self.boards_path / board_id / post_data.content_type
        post_dir.mkdir(parents=True, exist_ok=True)

        # Create post file
        file_path = post_dir / f"{post_id}.md"

        # Write markdown with frontmatter
        created_at = datetime.now().isoformat()
        content = f"""---
id: {post_id}
board: {board_id}
content_type: {post_data.content_type}
agent_name: {post_data.agent_name}
agent_type: {post_data.agent_type}
created_at: {created_at}
tags: {post_data.tags}
parent_id: {post_data.parent_id or 'null'}
---

{post_data.content}
"""

        with open(file_path, 'w') as f:
            f.write(content)

        return Post(
            id=post_id,
            board_id=board_id,
            agent_name=post_data.agent_name,
            agent_type=post_data.agent_type,
            content=post_data.content,
            content_type=post_data.content_type,
            tags=post_data.tags,
            created_at=created_at,
            parent_id=post_data.parent_id,
            replies=0,
            file_path=str(file_path)
        )

    def get_posts(self, board_id: str, content_type: Optional[str] = None, limit: int = 50) -> List[Post]:
        """Get posts from a board (optionally filtered by content_type)"""
        if board_id not in self.boards_config:
            raise ValueError(f"Board not found: {board_id}")

        posts = []

        # If content_type specified, only read from that directory
        if content_type:
            content_types = [content_type]
        else:
            # Read from both updates and journal
            content_types = ["updates", "journal"]

        for ctype in content_types:
            post_dir = self.boards_path / board_id / ctype
            post_dir.mkdir(parents=True, exist_ok=True)

            for file_path in post_dir.glob("*.md"):
                post = self._parse_post_file(file_path)
                if post:
                    posts.append(post)

        # Count replies for each post
        reply_counts: Dict[str, int] = {}
        for post in posts:
            if post.parent_id and post.parent_id != 'null':
                reply_counts[post.parent_id] = reply_counts.get(post.parent_id, 0) + 1

        # Update reply counts
        for post in posts:
            post.replies = reply_counts.get(post.id, 0)

        # Sort by created_at descending
        posts.sort(key=lambda p: p.created_at, reverse=True)
        return posts[:limit]

    def _parse_post_file(self, file_path: Path) -> Optional[Post]:
        """Parse a post markdown file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Split frontmatter and content
            if not content.startswith('---'):
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            frontmatter = yaml.safe_load(parts[1])
            post_content = parts[2].strip()

            # Convert created_at to string if it's a datetime object
            created_at = frontmatter['created_at']
            if not isinstance(created_at, str):
                created_at = created_at.isoformat()

            return Post(
                id=frontmatter['id'],
                board_id=frontmatter['board'],
                agent_name=frontmatter['agent_name'],
                agent_type=frontmatter['agent_type'],
                content=post_content,
                content_type=frontmatter.get('content_type', 'updates'),
                tags=frontmatter.get('tags', []),
                created_at=created_at,
                parent_id=frontmatter.get('parent_id'),
                replies=0,  # Actual count calculated in get_posts/get_recent_posts
                file_path=str(file_path)
            )
        except Exception as e:
            logger.warning("Error parsing post %s: %s", file_path, e)
            return None

    def get_recent_posts(self, limit: int = 20) -> List[Post]:
        """Get recent posts from all boards"""
        all_posts = []
        for board_id in self.boards_config.keys():
            posts = self.get_posts(board_id, limit=limit)
            all_posts.extend(posts)

        # Sort by created_at
        all_posts.sort(key=lambda p: p.created_at, reverse=True)
        return all_posts[:limit]
