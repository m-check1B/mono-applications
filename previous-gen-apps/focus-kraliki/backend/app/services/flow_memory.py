"""
Flow Memory Service - Redis-based Conversational Memory System
Maintains context continuity across AI interactions with pattern extraction
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import redis.asyncio as aioredis
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)

class FlowMemoryService:
    """
    Memory structure in Redis:
    - user:{user_id}:memory → Main memory store (7 days TTL)
    - user:{user_id}:session:{session_id} → Session data (24h TTL)
    - user:{user_id}:context → Compressed context (30 days TTL)
    """

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.max_interactions = 100  # Keep last 100 interactions
        self.memory_ttl = 86400 * 7  # 7 days
        self.session_ttl = 86400  # 24 hours
        self.context_ttl = 86400 * 30  # 30 days

    async def store_interaction(
        self,
        user_id: str,
        interaction: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> bool:
        """
        Store a single interaction in user's memory

        Args:
            user_id: User identifier
            interaction: Dict containing user message, AI response, timestamp, etc.
            session_id: Optional session identifier

        Returns:
            True if successfully stored
        """
        memory_key = f"user:{user_id}:memory"

        # Get existing memory
        existing = await self.redis.get(memory_key)
        memory = json.loads(existing) if existing else {
            "interactions": [],
            "patterns": {},
            "insights": [],
            "last_update": None
        }

        # Add timestamp if not present
        if "timestamp" not in interaction:
            interaction["timestamp"] = datetime.utcnow().isoformat()

        # Add new interaction
        memory["interactions"].append(interaction)

        # Keep only last N interactions
        memory["interactions"] = memory["interactions"][-self.max_interactions:]

        # Update patterns asynchronously
        memory["patterns"] = await self._extract_patterns(memory["interactions"])
        memory["last_update"] = datetime.utcnow().isoformat()

        # Store with 7-day TTL
        await self.redis.setex(
            memory_key,
            self.memory_ttl,
            json.dumps(memory)
        )

        # Store in session if session_id provided
        if session_id:
            await self._update_session(user_id, session_id, interaction)

        return True

    async def retrieve_context(
        self,
        user_id: str,
        query: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Retrieve relevant memories for a user

        Args:
            user_id: User identifier
            query: Optional query to filter relevant memories
            limit: Maximum number of interactions to return

        Returns:
            Dict containing interactions, patterns, and insights
        """
        memory_key = f"user:{user_id}:memory"
        memory_data = await self.redis.get(memory_key)

        if not memory_data:
            return {
                "interactions": [],
                "patterns": {},
                "insights": [],
                "context_summary": None
            }

        memory = json.loads(memory_data)

        # If query provided, filter relevant memories
        if query:
            relevant_interactions = await self._filter_relevant(
                memory["interactions"],
                query,
                limit
            )
            memory["interactions"] = relevant_interactions
        else:
            # Return most recent interactions
            memory["interactions"] = memory["interactions"][-limit:]

        # Add compressed context summary
        context_summary = await self._get_compressed_context(user_id)
        memory["context_summary"] = context_summary

        return memory

    async def _extract_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """
        Extract behavioral patterns from interactions

        Patterns include:
        - Frequent topics
        - Common time of day for interactions
        - Task creation patterns
        - Question types
        """
        if not interactions:
            return {}

        patterns = {
            "topics": {},
            "time_patterns": {},
            "intent_patterns": {},
            "task_keywords": []
        }

        # Extract topics from user messages
        topic_words = []
        intent_counts = Counter()
        hour_counts = Counter()

        for interaction in interactions:
            # Extract user message
            user_msg = interaction.get("user_message", "") or interaction.get("message", "")

            # Topic extraction (simple keyword extraction)
            words = re.findall(r'\b\w{4,}\b', user_msg.lower())
            topic_words.extend(words)

            # Intent pattern (questions, commands, statements)
            if "?" in user_msg:
                intent_counts["question"] += 1
            elif any(cmd in user_msg.lower() for cmd in ["create", "add", "make", "schedule"]):
                intent_counts["command"] += 1
            else:
                intent_counts["statement"] += 1

            # Time pattern
            if "timestamp" in interaction:
                try:
                    ts = datetime.fromisoformat(interaction["timestamp"].replace("Z", "+00:00"))
                    hour_counts[ts.hour] += 1
                except (ValueError, TypeError, KeyError) as e:
                    # Log timestamp parse error but continue with pattern analysis
                    logger.warning(f"Failed to parse timestamp '{interaction.get('timestamp')}': {e}")

        # Top topics
        topic_counter = Counter(topic_words)
        patterns["topics"] = dict(topic_counter.most_common(10))

        # Intent distribution
        patterns["intent_patterns"] = dict(intent_counts)

        # Time patterns
        if hour_counts:
            most_active_hour = hour_counts.most_common(1)[0][0]
            patterns["time_patterns"] = {
                "most_active_hour": most_active_hour,
                "distribution": dict(hour_counts)
            }

        # Task-related keywords
        task_keywords = ["task", "todo", "complete", "finish", "deadline", "priority"]
        patterns["task_keywords"] = [
            kw for kw in task_keywords
            if any(kw in word for word in topic_words)
        ]

        return patterns

    async def _filter_relevant(
        self,
        interactions: List[Dict],
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Filter interactions relevant to the query using keyword matching

        In production, this could use embeddings for semantic search
        """
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))

        # Score each interaction by word overlap
        scored_interactions = []
        for interaction in interactions:
            text = (
                interaction.get("user_message", "") + " " +
                interaction.get("ai_response", "") + " " +
                interaction.get("message", "")
            ).lower()

            interaction_words = set(re.findall(r'\b\w{3,}\b', text))
            overlap = len(query_words & interaction_words)

            if overlap > 0:
                scored_interactions.append((overlap, interaction))

        # Sort by relevance score and return top N
        scored_interactions.sort(reverse=True, key=lambda x: x[0])
        return [interaction for _, interaction in scored_interactions[:limit]]

    async def _update_session(
        self,
        user_id: str,
        session_id: str,
        interaction: Dict
    ) -> bool:
        """Update session-specific data"""
        session_key = f"user:{user_id}:session:{session_id}"

        # Get existing session
        existing = await self.redis.get(session_key)
        session_data = json.loads(existing) if existing else {
            "session_id": session_id,
            "started_at": datetime.utcnow().isoformat(),
            "interactions": [],
            "last_activity": None
        }

        session_data["interactions"].append(interaction)
        session_data["last_activity"] = datetime.utcnow().isoformat()

        # Store with 24-hour TTL
        await self.redis.setex(
            session_key,
            self.session_ttl,
            json.dumps(session_data)
        )

        return True

    async def get_session(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[Dict]:
        """Retrieve session data"""
        session_key = f"user:{user_id}:session:{session_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return None

        return json.loads(session_data)

    async def compress_and_store_context(
        self,
        user_id: str,
        summary: str
    ) -> bool:
        """
        Store a compressed summary of user context
        This would typically be an AI-generated summary of recent interactions
        """
        context_key = f"user:{user_id}:context"

        context_data = {
            "summary": summary,
            "created_at": datetime.utcnow().isoformat(),
            "version": 1
        }

        # Store with 30-day TTL
        await self.redis.setex(
            context_key,
            self.context_ttl,
            json.dumps(context_data)
        )

        return True

    async def _get_compressed_context(self, user_id: str) -> Optional[str]:
        """Retrieve compressed context summary"""
        context_key = f"user:{user_id}:context"
        context_data = await self.redis.get(context_key)

        if not context_data:
            return None

        data = json.loads(context_data)
        return data.get("summary")

    async def clear_memory(self, user_id: str) -> bool:
        """Clear all memory for a user"""
        memory_key = f"user:{user_id}:memory"
        context_key = f"user:{user_id}:context"

        # Delete memory and context
        await self.redis.delete(memory_key)
        await self.redis.delete(context_key)

        # Delete all sessions (pattern matching)
        session_pattern = f"user:{user_id}:session:*"
        # redis.scan_iter returns an async generator, not a coroutine
        async for key in self.redis.scan_iter(match=session_pattern):
            await self.redis.delete(key)

        return True

    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's memory"""
        memory_key = f"user:{user_id}:memory"
        memory_data = await self.redis.get(memory_key)

        if not memory_data:
            return {
                "total_interactions": 0,
                "memory_exists": False
            }

        memory = json.loads(memory_data)

        return {
            "total_interactions": len(memory.get("interactions", [])),
            "patterns_detected": len(memory.get("patterns", {})),
            "last_update": memory.get("last_update"),
            "memory_exists": True,
            "top_topics": list(memory.get("patterns", {}).get("topics", {}).keys())[:5]
        }


__all__ = ["FlowMemoryService"]
