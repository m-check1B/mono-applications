"""Voice Arena Service for 1:1 Voice Interface Training.

This service manages practice sessions where trainees interact with AI personas
simulating customer scenarios for call center training.
"""

import logging
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ArenaPersona(str, Enum):
    """Available AI personas for practice sessions."""

    ANGRY_CUSTOMER = "angry_customer"
    CURIOUS_LEARNER = "curious_learner"
    CONFUSED_USER = "confused_user"
    SATISFIED_CLIENT = "satisfied_client"
    PERSISTENT_ISSUE_REPORTER = "persistent_issue_reporter"


class ArenaSessionState(str, Enum):
    """Session states."""

    WAITING = "waiting"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ArenaPersonaConfig(BaseModel):
    """Configuration for an AI persona."""

    name: str
    persona_type: ArenaPersona
    behavior_prompt: str
    response_style: str
    emotional_state: str
    escalation_triggers: list[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Angry Customer - Billing Dispute",
                "persona_type": "angry_customer",
                "behavior_prompt": "You are a frustrated customer disputing a billing charge. You are impatient and demand immediate resolution. You speak loudly and quickly, interrupting frequently.",
                "response_style": "aggressive, demanding, quick-speaking",
                "emotional_state": "frustrated, angry, impatient",
                "escalation_triggers": [
                    "I'll transfer you to a supervisor",
                    "Let me check with my manager",
                    "This is taking too long",
                ],
            }
        }


class ArenaSession(BaseModel):
    """A practice session in the voice arena."""

    id: UUID = Field(default_factory=uuid.uuid4)
    persona_config: ArenaPersonaConfig
    state: ArenaSessionState = ArenaSessionState.WAITING
    trainee_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    transcript: list[dict[str, Any]] = Field(default_factory=list)
    scorecard: dict[str, Any] | None = None
    is_recording: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "persona_config": {"name": "Angry Customer", "persona_type": "angry_customer"},
                "state": "active",
                "created_at": "2025-12-24T08:00:00Z",
                "transcript": [],
            }
        }


# Predefined personas
PERSONA_TEMPLATES = {
    ArenaPersona.ANGRY_CUSTOMER: ArenaPersonaConfig(
        name="Angry Customer - Billing Dispute",
        persona_type=ArenaPersona.ANGRY_CUSTOMER,
        behavior_prompt="You are a frustrated customer disputing an unexpected charge on your bill. You are impatient and demand immediate resolution. You speak quickly, interrupt frequently, and raise your voice. You want answers NOW, not excuses.",
        response_style="aggressive, demanding, fast-paced with interruptions",
        emotional_state="frustrated, angry, impatient",
        escalation_triggers=[
            "I'll transfer you to a supervisor",
            "Let me check with my manager",
            "This is taking too long",
        ],
    ),
    ArenaPersona.CURIOUS_LEARNER: ArenaPersonaConfig(
        name="Curious Learner - New Service",
        persona_type=ArenaPersona.CURIOUS_LEARNER,
        behavior_prompt="You are a curious potential customer asking about a new service offering. You ask detailed questions about features, pricing, and how it works. You are friendly but thorough, wanting to understand everything before making a decision.",
        response_style="friendly, inquisitive, thoughtful with pauses for consideration",
        emotional_state="interested, cautious, open-minded",
        escalation_triggers=[],
    ),
    ArenaPersona.CONFUSED_USER: ArenaPersonaConfig(
        name="Confused User - Technical Support",
        persona_type=ArenaPersona.CONFUSED_USER,
        behavior_prompt="You are a non-technical user experiencing a technical issue. You don't understand the technical jargon being used. You're confused about what to do next and need step-by-step guidance. You repeat yourself and ask the same questions multiple times.",
        response_style="uncertain, repetitive, hesitant, seeking clarity",
        emotional_state="confused, overwhelmed, seeking help",
        escalation_triggers=[
            "Can you restart your computer?",
            "Are you on WiFi or ethernet?",
            "Let me connect you to a specialist",
        ],
    ),
    ArenaPersona.SATISFIED_CLIENT: ArenaPersonaConfig(
        name="Satisfied Client - Post-Sale Follow-up",
        persona_type=ArenaPersona.SATISFIED_CLIENT,
        behavior_prompt="You are a satisfied customer following up on a successful purchase. You're happy with the service but want to confirm some details about delivery and setup. You're friendly, appreciative, and ask quick confirmatory questions.",
        response_style="friendly, appreciative, quick and positive",
        emotional_state="satisfied, happy, confident",
        escalation_triggers=[],
    ),
    ArenaPersona.PERSISTENT_ISSUE_REPORTER: ArenaPersonaConfig(
        name="Persistent Issue Reporter - Recurring Problem",
        persona_type=ArenaPersona.PERSISTENT_ISSUE_REPORTER,
        behavior_prompt="You are a customer reporting a SAME issue for the third time. You're frustrated that the problem keeps happening despite previous promises to fix it. You're skeptical of new assurances and want to speak to someone with authority who can guarantee resolution.",
        response_style="skeptical, frustrated, demanding guarantees and documentation",
        emotional_state="angry, distrustful, demanding",
        escalation_triggers=[
            "I understand your frustration",
            "This time I personally will oversee the fix",
            "Let me escalate this to our technical team leader",
        ],
    ),
}


class VoiceArenaService:
    """Voice Arena service for AI-powered training scenarios."""

    def __init__(self):
        """Initialize voice arena service."""
        self._active_sessions: dict[UUID, ArenaSession] = {}
        self._available_personas: dict[str, ArenaPersonaConfig] = {
            k.value: v for k, v in PERSONA_TEMPLATES.items()
        }

    async def create_session(
        self, persona_type: ArenaPersona, trainee_id: str | None = None
    ) -> ArenaSession:
        """Create a new arena practice session.

        Args:
            persona_type: Type of persona to use
            trainee_id: Optional trainee identifier

        Returns:
            Arena session configuration
        """
        persona = self._available_personas.get(str(persona_type))
        if not persona:
            raise ValueError(f"Unknown persona type: {persona_type}")

        session = ArenaSession(
            persona_config=persona, state=ArenaSessionState.WAITING, trainee_id=trainee_id
        )

        self._active_sessions[session.id] = session
        logger.info(f"Created arena session {session.id} with persona {persona_type}")
        return session

    async def start_session(self, session_id: UUID) -> None:
        """Start an arena session.

        Args:
            session_id: Session identifier
        """
        if session_id not in self._active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._active_sessions[session_id]
        session.state = ArenaSessionState.ACTIVE
        session.started_at = datetime.now(UTC)
        logger.info(f"Started arena session {session_id}")

    async def end_session(
        self, session_id: UUID, scorecard: dict[str, Any] | None = None
    ) -> None:
        """End an arena session.

        Args:
            session_id: Session identifier
            scorecard: Optional performance scorecard
        """
        if session_id not in self._active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._active_sessions[session_id]
        session.state = ArenaSessionState.COMPLETED
        session.ended_at = datetime.now(UTC)
        session.scorecard = scorecard

        if session.started_at and session.ended_at:
            duration = (session.ended_at - session.started_at).total_seconds()
            session.duration_seconds = int(duration)

        logger.info(f"Ended arena session {session_id}, duration: {session.duration_seconds}s")

    async def add_transcript_entry(self, session_id: UUID, role: str, content: str) -> None:
        """Add a transcript entry to a session.

        Args:
            session_id: Session identifier
            role: Speaker role ('trainee' or 'persona')
            content: Spoken content
        """
        if session_id not in self._active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._active_sessions[session_id]
        session.transcript.append(
            {"role": role, "content": content, "timestamp": datetime.now(UTC).isoformat()}
        )
        logger.debug(f"Added transcript entry to session {session_id}")

    async def get_session(self, session_id: UUID) -> ArenaSession | None:
        """Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Arena session or None
        """
        return self._active_sessions.get(session_id)

    async def get_available_personas(self) -> list[ArenaPersonaConfig]:
        """Get list of available personas.

        Returns:
            List of persona configurations
        """
        return list(self._available_personas.values())

    def get_active_sessions(self) -> list[ArenaSession]:
        """Get all active sessions.

        Returns:
            List of active arena sessions
        """
        return [
            session
            for session in self._active_sessions.values()
            if session.state in [ArenaSessionState.ACTIVE, ArenaSessionState.WAITING]
        ]

    async def generate_persona_response(self, session_id: UUID, trainee_input: str) -> str:
        """Generate AI persona response based on trainee input.

        Args:
            session_id: Session identifier
            trainee_input: What's trainee said

        Returns:
            AI-generated response
        """
        if session_id not in self._active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._active_sessions[session_id]
        persona = session.persona_config

        responses = self._get_rule_based_responses(persona)

        last_trainee_input = session.transcript[-1]["content"] if session.transcript else ""

        response = self._select_contextual_response(
            responses, persona, trainee_input, last_trainee_input
        )

        await self.add_transcript_entry(session_id, "persona", response)
        return response

    def _get_rule_based_responses(self, persona: ArenaPersonaConfig) -> dict[str, list[str]]:
        """Get rule-based responses for a persona.

        Args:
            persona: Persona configuration

        Returns:
            Dictionary mapping input types to response lists
        """
        if persona.persona_type == ArenaPersona.ANGRY_CUSTOMER:
            return {
                "greeting": [
                    "I've been waiting on hold for 10 minutes! This is ridiculous.",
                    "I need to speak to someone who can actually help me, not listen to excuses.",
                    "Look, I don't have all day. Can we resolve this NOW?",
                ],
                "apology": [
                    "Fine, sorry I raised my voice.",
                    "I just want this fixed, okay?",
                    "Let's just move forward.",
                ],
                "escalation": [
                    "Transfer me to your supervisor NOW.",
                    "I want to speak to someone in charge.",
                    "This is unacceptable.",
                ],
                "resolution": [
                    "Okay, that sounds reasonable.",
                    "Finally, thank you.",
                    "I appreciate that.",
                ],
            }
        elif persona.persona_type == ArenaPersona.CURIOUS_LEARNER:
            return {
                "greeting": [
                    "Hi, I'm calling about this new service I heard about.",
                    "Can you tell me more about how it works?",
                    "I'm interested but have some questions first.",
                ],
                "questions": [
                    "What exactly does this feature do?",
                    "How much does it cost?",
                    "Is there a free trial?What makes this different from competitors?",
                ],
                "positive": ["That makes sense.", "Oh, I see now.", "Interesting, tell me more."],
            }
        elif persona.persona_type == ArenaPersona.CONFUSED_USER:
            return {
                "greeting": [
                    "Hello? I think I'm having a problem with my account.",
                    "I'm not sure what I did wrong here.",
                    "Can you help me figure this out?",
                ],
                "confusion": [
                    "I don't understand what you mean by that.",
                    "Wait, can you say that again?",
                    "I'm confused, step by step please?",
                    "What do you want me to click?",
                ],
                "escalation": [
                    "Can I just talk to someone else?",
                    "This is too complicated for me.",
                    "Maybe I should just call back later.",
                ],
            }
        elif persona.persona_type == ArenaPersona.SATISFIED_CLIENT:
            return {
                "greeting": [
                    "Hi, I'm just confirming some details about my order.",
                    "Everything seems to be working great, thanks.",
                    "I just wanted to double-check delivery times.",
                ],
                "confirmation": [
                    "Perfect, that's what I understood.",
                    "Great, thank you for clarifying.",
                    "Excellent, I'm all set then.",
                ],
            }
        elif persona.persona_type == ArenaPersona.PERSISTENT_ISSUE_REPORTER:
            return {
                "greeting": [
                    "Yes, I'm calling about the same problem again.",
                    "This is the third time I'm reporting this.",
                    "I thought we fixed this last week?",
                ],
                "complaint": [
                    "It's happening AGAIN.",
                    "I was promised this wouldn't happen.",
                    "Why does this keep occurring?",
                    "I want to speak to someone who can guarantee a fix.",
                ],
                "skeptical": [
                    "I've heard that before.",
                    "How do I know this time it's different?",
                    "I need some assurance here.",
                ],
                "resolution": [
                    "Well, if you're personally handling it, okay.",
                    "I'll give it one more try then.",
                    "Fine, let's document this escalation.",
                ],
            }

        return {}

    def _select_contextual_response(
        self,
        responses: dict[str, list[str]],
        persona: ArenaPersonaConfig,
        trainee_input: str,
        last_trainee_input: str,
    ) -> str:
        """Select a response based on context.

        Args:
            responses: Available response categories
            persona: Persona configuration
            trainee_input: Current trainee input
            last_trainee_input: Previous trainee input

        Returns:
            Selected response
        """
        input_lower = trainee_input.lower()

        if any(word in input_lower for word in ["hello", "hi", "hey"]):
            return responses.get("greeting", ["Hello."])[0]

        if any(word in input_lower for word in ["sorry", "apologize", "my bad"]):
            return responses.get("apology", ["I understand."])[0]

        if any(word in input_lower for word in ["understand", "got it", "makes sense", "ok"]):
            if "resolution" in responses:
                return responses["resolution"][0]

        if any(word in input_lower for word in ["transfer", "supervisor", "manager"]):
            if "escalation" in responses:
                return responses["escalation"][0]

        if any(word in input_lower for word in ["question", "what", "how", "why"]):
            if "questions" in responses:
                return responses["questions"][0]

        if "aggressive" in persona.response_style:
            return "I need an answer, not more waiting. Can you help me or not?"

        return "I see. Can you continue?"
