"""
Speak by Kraliki - AI Conversation Service
Handles the AI-powered voice/text conversations with employees

Platform 2026: Uses ai-core for unified LLM abstraction with Gemini fallback
"""

import logging
import random
from datetime import datetime
from typing import AsyncGenerator

from app.core.config import settings

logger = logging.getLogger(__name__)

# Platform 2026: Try ai-core first, fall back to direct Gemini SDK
_use_ai_core = False
_gemini_provider = None

try:
    from ai_core import create_provider, LLMProvider, Message, MessageRole, CompletionConfig
    _use_ai_core = True
except ImportError:
    pass


def get_gemini_provider():
    """Get or create Gemini provider instance (ai-core)."""
    global _gemini_provider
    if _gemini_provider is None and _use_ai_core:
        _gemini_provider = create_provider(
            LLMProvider.GEMINI,
            api_key=settings.gemini_api_key
        )
    return _gemini_provider

# Filler sounds for latency handling (v2.0)
FILLER_SOUNDS = [
    "Hmm, rozumim...",
    "Momentik...",
    "Diky, premyslim...",
    "Jasne...",
    "Aha...",
    "Rozumim...",
]

# Default questions (Czech)
DEFAULT_QUESTIONS = [
    {
        "id": 1,
        "question": "Jak se ti dari v praci tento mesic?",
        "follow_up_count": 1
    },
    {
        "id": 2,
        "question": "Co te nejvic tesi nebo motivuje?",
        "follow_up_count": 1
    },
    {
        "id": 3,
        "question": "Je neco, co te frustruje nebo te trapi?",
        "follow_up_count": 2
    },
    {
        "id": 4,
        "question": "Jak hodnotis spolupraci s tymem a nadrizenymi?",
        "follow_up_count": 1
    },
    {
        "id": 5,
        "question": "Je jeste neco, co bys chtel/a rict?",
        "follow_up_count": 0
    },
]

# System prompt for AI
SYSTEM_PROMPT_TEMPLATE = """Jsi pratelsky AI asistent pro mesicni check-in se zamestnancem.
Cil: zjistit jak se mu dari, co ho tesi, co ho trapi.

PRAVIDLA:
- Mluv cesky, prirozene, pratelsky
- Odpovedi KRATKE (1-2 vety max) - rychly dialog
- Ptej se follow-up jen na dulezite veci
- Neopakuj otazky
- Nikdy neslibuj zmeny - jsi jen posluchac
- Cely rozhovor MAX 5-7 minut

STRUKTURA:
1. Kratky pozdrav (10 sec)
2. 4-5 core otazek (5 min)
3. Prostor pro cokoliv (1 min)
4. Podekovani (10 sec)

KONTEXT:
- Zamestnanec: {employee_first_name}
- Firma: {company_name}
- Oddeleni: {department_name}

Aktualni otazka: {current_question}
Predchozi odpovedi: {previous_responses}
"""


class AIConversationService:
    """Service for managing AI conversations with employees."""

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model

    def get_filler_sound(self) -> str:
        """Get random filler sound for latency handling."""
        return random.choice(FILLER_SOUNDS)

    def get_greeting(self, employee_name: str) -> str:
        """Generate greeting message."""
        greetings = [
            f"Ahoj {employee_name}! Diky, ze sis udelal/a cas. Jak se mas?",
            f"Ahoj {employee_name}! Dekuji za tvuj cas. Jak ti to jde?",
            f"Ahoj {employee_name}! Rad/a te vidim. Jak se ti dari?",
        ]
        return random.choice(greetings)

    def get_farewell(self) -> str:
        """Generate farewell message."""
        farewells = [
            "Mockrat diky za tvuj cas a uprimnost! Tvoje zpetna vazba je pro nas dulezita.",
            "Dekuji za rozhovor! Vazime si tve zpetne vazby.",
            "Diky moc! Tvuj nazor je pro nas cenny. Mej se hezky!",
        ]
        return random.choice(farewells)

    async def generate_response(
        self,
        employee_name: str,
        company_name: str,
        department_name: str,
        current_question: str,
        user_message: str,
        conversation_history: list[dict],
        custom_prompt: str | None = None
    ) -> str:
        """Generate AI response to employee message."""
        # Build system prompt
        system_prompt = (custom_prompt or SYSTEM_PROMPT_TEMPLATE).format(
            employee_first_name=employee_name,
            company_name=company_name,
            department_name=department_name or "Nezname",
            current_question=current_question,
            previous_responses=self._format_history(conversation_history)
        )

        if not self.api_key:
            return self._generate_fallback_response(user_message, current_question)

        # Platform 2026: Try ai-core first
        if _use_ai_core:
            try:
                provider = get_gemini_provider()
                if provider:
                    # Build messages for ai-core
                    ai_messages = [Message(role=MessageRole.SYSTEM, content=system_prompt)]
                    for turn in conversation_history:
                        role = MessageRole.ASSISTANT if turn["role"] == "ai" else MessageRole.USER
                        ai_messages.append(Message(role=role, content=turn["content"]))
                    ai_messages.append(Message(role=MessageRole.USER, content=user_message))

                    config = CompletionConfig(
                        model=self.model,
                        max_tokens=300,
                        temperature=0.7
                    )
                    result = await provider.complete(ai_messages, config)
                    return result.content
            except Exception as e:
                logger.warning(f"ai-core Gemini error: {e}, falling back to direct SDK")

        # Fallback: Direct Gemini SDK
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)

            # Build messages
            messages = [{"role": "user", "parts": [system_prompt]}]
            for turn in conversation_history:
                role = "model" if turn["role"] == "ai" else "user"
                messages.append({"role": role, "parts": [turn["content"]]})
            messages.append({"role": "user", "parts": [user_message]})

            response = await model.generate_content_async(
                messages,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 300,
                }
            )
            return response.text
        except Exception as e:
            logger.exception(f"Gemini API error: {e}")
            return self._generate_fallback_response(user_message, current_question)

    def _format_history(self, history: list[dict]) -> str:
        """Format conversation history for prompt."""
        if not history:
            return "Zadne"
        lines = []
        for turn in history[-6:]:  # Last 6 turns
            role = "Zamestnanec" if turn["role"] == "user" else "AI"
            lines.append(f"{role}: {turn['content'][:100]}")
        return "\n".join(lines)

    def _generate_fallback_response(self, user_message: str, current_question: str) -> str:
        """Generate fallback response when API is unavailable."""
        # Simple acknowledgment responses
        responses = [
            "Rozumim, diky za sdileni. Muzes mi rict vic?",
            "Aha, to je zajimave. Chces k tomu neco dodat?",
            "Chapu. Jak se s tim vyrovnavas?",
            "Dekuji za uprimnost. Je jeste neco, co bys chtel/a rict?",
        ]
        return random.choice(responses)

    async def stream_response(
        self,
        employee_name: str,
        company_name: str,
        department_name: str,
        current_question: str,
        user_message: str,
        conversation_history: list[dict],
    ) -> AsyncGenerator[str, None]:
        """Stream AI response for real-time voice synthesis."""
        response = await self.generate_response(
            employee_name,
            company_name,
            department_name,
            current_question,
            user_message,
            conversation_history,
        )
        # Stream word by word for TTS
        words = response.split()
        buffer = ""
        for word in words:
            buffer += word + " "
            if len(buffer) > 20 or word.endswith((".", "?", "!", ",")):
                yield buffer.strip()
                buffer = ""
        if buffer.strip():
            yield buffer.strip()
