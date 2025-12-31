"""
Shadow Analysis Service - Jungian Archetype-Based Personality Insights
Implements 30-day progressive unlock system for shadow work
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json
import uuid

from app.models.shadow_profile import ShadowProfile, ShadowInsight
from app.models.task import Task
from app.schemas.shadow import (
    ShadowProfileResponse,
    ShadowInsightResponse,
    DailyInsightResponse,
    ProgressResponse,
    UnlockResponse
)

# Jungian Archetypes with shadow aspects
ARCHETYPES = {
    "warrior": {
        "traits": ["courage", "discipline", "protection", "determination", "strength"],
        "shadow": ["aggression", "rigidity", "burnout", "need_for_control", "excessive_competitiveness"],
        "growth_path": "Learn when to rest and trust others. Balance strength with vulnerability.",
        "keywords": ["achieve", "fight", "protect", "win", "conquer", "complete", "finish"]
    },
    "sage": {
        "traits": ["wisdom", "analysis", "teaching", "objectivity", "insight"],
        "shadow": ["detachment", "overthinking", "arrogance", "paralysis_by_analysis", "emotional_avoidance"],
        "growth_path": "Balance knowledge with emotion and action. Trust your heart as well as your mind.",
        "keywords": ["think", "analyze", "understand", "learn", "research", "study", "read"]
    },
    "lover": {
        "traits": ["passion", "connection", "creativity", "empathy", "appreciation"],
        "shadow": ["jealousy", "dependency", "boundary_issues", "fear_of_abandonment", "possessiveness"],
        "growth_path": "Develop self-love and healthy boundaries. Find security within yourself.",
        "keywords": ["love", "connect", "feel", "share", "relate", "care", "enjoy"]
    },
    "creator": {
        "traits": ["innovation", "expression", "vision", "originality", "imagination"],
        "shadow": ["perfectionism", "self_criticism", "isolation", "fear_of_judgment", "procrastination"],
        "growth_path": "Embrace imperfection and collaboration. Share your work even when it's not perfect.",
        "keywords": ["create", "design", "build", "make", "innovate", "imagine", "express"]
    },
    "caregiver": {
        "traits": ["compassion", "nurturing", "service", "generosity", "support"],
        "shadow": ["martyrdom", "enabling", "neglecting_self", "codependency", "burnout"],
        "growth_path": "Learn to receive and set limits. You can't pour from an empty cup.",
        "keywords": ["help", "support", "care", "nurture", "give", "assist", "serve"]
    },
    "explorer": {
        "traits": ["independence", "curiosity", "adventure", "freedom", "spontaneity"],
        "shadow": ["restlessness", "escapism", "commitment_issues", "irresponsibility", "running_away"],
        "growth_path": "Find meaning in stillness and depth. True freedom includes commitment.",
        "keywords": ["explore", "discover", "travel", "try", "experiment", "wander", "seek"]
    }
}


class ShadowAnalyzerService:
    """Service for shadow analysis and progressive insight unlocking"""

    def __init__(self, db: Session):
        self.db = db

    async def create_profile(self, user_id: str) -> ShadowProfileResponse:
        """Create a new shadow profile for user"""
        # Check if profile already exists
        existing = self.db.query(ShadowProfile).filter(ShadowProfile.user_id == user_id).first()
        if existing:
            return ShadowProfileResponse.from_orm(existing)

        # Determine primary archetype based on user behavior
        archetype = await self._determine_archetype(user_id)

        # Create profile
        profile = ShadowProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            archetype=archetype,
            unlock_day=1,
            total_days=30,
            insights_data={},
            patterns={}
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        # Generate all 30 days of insights
        await self._generate_initial_insights(profile)

        return ShadowProfileResponse.from_orm(profile)

    async def _determine_archetype(self, user_id: str) -> str:
        """
        Determine user's primary Jungian archetype based on task patterns

        Analysis approach:
        1. Analyze task titles and descriptions for keywords
        2. Look at task completion patterns
        3. Examine time management style
        4. Score each archetype and return highest
        """
        # Get user's tasks
        tasks = self.db.query(Task).filter(Task.userId == user_id).limit(100).all()

        if not tasks:
            # Default to explorer for new users
            return "explorer"

        # Score each archetype based on keyword matches
        scores = {archetype: 0 for archetype in ARCHETYPES.keys()}

        for task in tasks:
            text = (task.title or "").lower() + " " + (task.description or "").lower()

            for archetype, data in ARCHETYPES.items():
                for keyword in data["keywords"]:
                    if keyword in text:
                        scores[archetype] += 1

        # Also analyze completion patterns
        completed_tasks = [t for t in tasks if t.status == "completed"]
        if len(completed_tasks) / max(len(tasks), 1) > 0.8:
            scores["warrior"] += 10  # High completion = warrior trait

        # Analyze task complexity (longer descriptions = sage)
        avg_desc_length = sum(len(t.description or "") for t in tasks) / max(len(tasks), 1)
        if avg_desc_length > 100:
            scores["sage"] += 5

        # Return archetype with highest score
        primary_archetype = max(scores, key=scores.get)
        return primary_archetype

    async def _generate_initial_insights(self, profile: ShadowProfile):
        """Generate 30 days of progressive insights"""
        archetype_info = ARCHETYPES[profile.archetype]

        # Template insights for different stages
        awareness_templates = [
            "Notice when you {shadow_trait}. This is your shadow trying to protect you from feeling {fear}.",
            "Pay attention to moments when {trait} becomes excessive. The shadow emerges when strengths become rigid.",
            "Observe how {shadow_trait} shows up in your daily life. What triggers this pattern?",
            "When you find yourself {shadow_trait}, pause and ask: What am I really afraid of?",
            "Your tendency toward {shadow_trait} often masks a deeper need for {growth_need}.",
            "Notice the cost of {shadow_trait}. How does it affect your relationships and well-being?",
            "Track situations where {trait} turns into {shadow_trait}. What's the tipping point?",
            "Become aware of the stories you tell yourself that justify {shadow_trait}.",
            "Pay attention to physical sensations when {shadow_trait} emerges. Your body knows.",
            "Notice who in your life reflects your shadow back to you through their {shadow_trait}."
        ]

        understanding_templates = [
            "Your {shadow_trait} likely developed as a protection mechanism. What were you protecting yourself from?",
            "Explore the origins of {shadow_trait}. When did you first learn this pattern?",
            "Your shadow's {shadow_trait} is not the enemy - it's a part of you seeking integration.",
            "The intensity of {shadow_trait} reflects the strength of what you're defending against.",
            "Your {archetype} archetype's shadow emerges when you feel threatened in your core identity.",
            "Compassionately explore what {shadow_trait} has cost you and what it has protected you from.",
            "The opposite of {trait} isn't {shadow_trait} - it's the fear of being without {trait}.",
            "Your shadow's {shadow_trait} is asking: What if I'm not enough without this defense?",
            "Understanding doesn't mean accepting {shadow_trait} - it means seeing its purpose clearly.",
            "The shadow isn't something to fix, but something to understand and integrate."
        ]

        integration_templates = [
            "Practice the opposite of {shadow_trait}: {growth_action}. Start small.",
            "When {shadow_trait} arises, respond with {growth_response} instead of resistance.",
            "Integration means holding both {trait} and its opposite. You contain multitudes.",
            "Develop a new relationship with {shadow_trait} - not as enemy, but as teacher.",
            "Your {growth_path}. This is your path to wholeness.",
            "Transform {shadow_trait} through conscious awareness and compassionate action.",
            "You are not your shadow. You are the awareness that can hold both light and dark.",
            "Practice embodying {growth_quality} - the integrated form of your {archetype} energy.",
            "The goal isn't eliminating {shadow_trait}, but choosing consciously when to express it.",
            "Celebrate progress: You're now aware of patterns that once controlled you unconsciously."
        ]

        all_templates = []
        # Days 1-10: Awareness
        for i in range(10):
            all_templates.append(("awareness", awareness_templates[i % len(awareness_templates)]))
        # Days 11-20: Understanding
        for i in range(10):
            all_templates.append(("understanding", understanding_templates[i % len(understanding_templates)]))
        # Days 21-30: Integration
        for i in range(10):
            all_templates.append(("integration", integration_templates[i % len(integration_templates)]))

        # Generate insights for all 30 days
        for day in range(1, 31):
            insight_type, template = all_templates[day - 1]

            # Fill template with archetype-specific content
            content = template.format(
                archetype=profile.archetype,
                trait=archetype_info["traits"][day % len(archetype_info["traits"])],
                shadow_trait=archetype_info["shadow"][day % len(archetype_info["shadow"])],
                growth_path=archetype_info["growth_path"],
                fear="inadequacy" if day % 3 == 0 else "rejection" if day % 3 == 1 else "vulnerability",
                growth_need="connection" if day % 3 == 0 else "authenticity" if day % 3 == 1 else "self-acceptance",
                growth_action="rest and receive" if profile.archetype == "warrior" else "take action" if profile.archetype == "sage" else "set boundaries",
                growth_response="curiosity" if day % 2 == 0 else "compassion",
                growth_quality="balanced strength" if profile.archetype == "warrior" else "embodied wisdom"
            )

            insight = ShadowInsight(
                id=str(uuid.uuid4()),
                profile_id=profile.id,
                day=day,
                insight_type=insight_type,
                content=content,
                unlocked=(day == 1),  # Only day 1 unlocked initially
                unlocked_at=datetime.utcnow() if day == 1 else None
            )
            self.db.add(insight)

        self.db.commit()

    async def get_profile(self, user_id: str) -> Optional[ShadowProfileResponse]:
        """Get user's shadow profile"""
        profile = self.db.query(ShadowProfile).filter(ShadowProfile.user_id == user_id).first()
        if not profile:
            return None
        return ShadowProfileResponse.from_orm(profile)

    async def get_daily_insight(self, user_id: str, day: Optional[int] = None) -> DailyInsightResponse:
        """Get shadow insight for specific day"""
        profile = self.db.query(ShadowProfile).filter(ShadowProfile.user_id == user_id).first()

        if not profile:
            # Auto-create profile if it doesn't exist
            await self.create_profile(user_id)
            profile = self.db.query(ShadowProfile).filter(ShadowProfile.user_id == user_id).first()

        # Use current unlock day if not specified
        if day is None:
            day = profile.unlock_day

        # Check if day is valid
        if day < 1 or day > 30:
            return DailyInsightResponse(
                locked=True,
                day=day,
                progress=f"{profile.unlock_day}/{profile.total_days}",
                message="Invalid day number"
            )

        # Check if day is unlocked
        if day > profile.unlock_day:
            return DailyInsightResponse(
                locked=True,
                day=day,
                archetype=profile.archetype,
                progress=f"{profile.unlock_day}/{profile.total_days}",
                message=f"This insight unlocks on day {day}. You are currently on day {profile.unlock_day}."
            )

        # Get insight for the day
        insight = self.db.query(ShadowInsight).filter(
            and_(
                ShadowInsight.profile_id == profile.id,
                ShadowInsight.day == day
            )
        ).first()

        if not insight:
            return DailyInsightResponse(
                locked=True,
                day=day,
                progress=f"{profile.unlock_day}/{profile.total_days}",
                message="Insight not found for this day"
            )

        return DailyInsightResponse(
            locked=False,
            day=day,
            insight=ShadowInsightResponse.from_orm(insight),
            archetype=profile.archetype,
            progress=f"{profile.unlock_day}/{profile.total_days}"
        )

    async def unlock_next_day(self, user_id: str) -> UnlockResponse:
        """Unlock the next day's insight"""
        profile = self.db.query(ShadowProfile).filter(ShadowProfile.user_id == user_id).first()

        if not profile:
            return UnlockResponse(
                unlocked=False,
                message="No shadow profile found. Please create a profile first."
            )

        # Check if all days are already unlocked
        if profile.unlock_day >= profile.total_days:
            return UnlockResponse(
                unlocked=False,
                message="All insights are already unlocked!"
            )

        # Check if enough time has passed (24 hours)
        # For demo purposes, we'll allow immediate unlocking
        # In production, add time check here

        # Unlock next day
        profile.unlock_day += 1

        # Mark insight as unlocked
        insight = self.db.query(ShadowInsight).filter(
            and_(
                ShadowInsight.profile_id == profile.id,
                ShadowInsight.day == profile.unlock_day
            )
        ).first()

        if insight:
            insight.unlocked = True
            insight.unlocked_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(profile)
        if insight:
            self.db.refresh(insight)

        return UnlockResponse(
            unlocked=True,
            new_day=profile.unlock_day,
            insight=ShadowInsightResponse.from_orm(insight) if insight else None,
            message=f"Day {profile.unlock_day} unlocked! New insight available."
        )

    async def get_progress(self, user_id: str) -> Optional[ProgressResponse]:
        """Get overall shadow work progress"""
        profile = self.db.query(ShadowProfile).filter(ShadowProfile.user_id == user_id).first()

        if not profile:
            return None

        unlocked_count = self.db.query(ShadowInsight).filter(
            and_(
                ShadowInsight.profile_id == profile.id,
                ShadowInsight.unlocked == True
            )
        ).count()

        return ProgressResponse(
            unlock_day=profile.unlock_day,
            total_days=profile.total_days,
            unlocked_insights=unlocked_count,
            archetype=profile.archetype,
            completion_percentage=(profile.unlock_day / profile.total_days) * 100
        )

    async def get_all_unlocked_insights(self, user_id: str) -> List[ShadowInsightResponse]:
        """Get all unlocked insights for user"""
        profile = self.db.query(ShadowProfile).filter(ShadowProfile.user_id == user_id).first()

        if not profile:
            return []

        insights = self.db.query(ShadowInsight).filter(
            and_(
                ShadowInsight.profile_id == profile.id,
                ShadowInsight.unlocked == True
            )
        ).order_by(ShadowInsight.day).all()

        return [ShadowInsightResponse.from_orm(i) for i in insights]
