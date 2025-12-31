"""Jungian dream analysis service.

Uses LLM to provide deep symbolic interpretation of dreams
through a Jungian psychological lens.
"""
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional

import google.generativeai as genai

from app.core.config import settings


logger = logging.getLogger(__name__)


@dataclass
class DreamAnalysis:
    """Complete dream interpretation."""
    dream_text: str
    symbols: list[dict]  # [{symbol, meaning, archetype}]
    archetypes: list[str]  # Shadow, Anima/Animus, Self, etc.
    themes: list[str]
    emotional_tone: str
    interpretation: str
    personal_message: str
    questions_to_consider: list[str]
    cosmic_correlation: Optional[str] = None  # Link to current sensitivity
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)

    def to_summary(self) -> str:
        """Generate readable summary."""
        lines = [
            "Dream Analysis",
            "=" * 40,
            "",
            f"Emotional Tone: {self.emotional_tone}",
            "",
            "Key Symbols:",
        ]

        for sym in self.symbols[:5]:
            lines.append(f"  - {sym['symbol']}: {sym['meaning']}")
            if sym.get('archetype'):
                lines.append(f"    (Archetype: {sym['archetype']})")

        lines.extend([
            "",
            f"Archetypes Present: {', '.join(self.archetypes)}",
            "",
            f"Themes: {', '.join(self.themes)}",
            "",
            "Interpretation:",
            self.interpretation,
            "",
            "Personal Message:",
            self.personal_message,
        ])

        if self.cosmic_correlation:
            lines.extend([
                "",
                "Cosmic Connection:",
                self.cosmic_correlation
            ])

        if self.questions_to_consider:
            lines.extend([
                "",
                "Questions to Consider:",
            ])
            for q in self.questions_to_consider:
                lines.append(f"  - {q}")

        return "\n".join(lines)


JUNGIAN_ARCHETYPES = [
    "The Shadow",  # Repressed aspects of self
    "The Anima",  # Feminine inner personality (in men)
    "The Animus",  # Masculine inner personality (in women)
    "The Self",  # Wholeness, integration
    "The Persona",  # Social mask
    "The Hero",  # Overcoming obstacles
    "The Mother",  # Nurturing, protection
    "The Father",  # Authority, guidance
    "The Child",  # Innocence, new beginnings
    "The Wise Old Man/Woman",  # Wisdom, guidance
    "The Trickster",  # Chaos, transformation
    "The Maiden",  # Purity, potential
]

DREAM_ANALYSIS_PROMPT = """You are a Jungian dream analyst providing deep psychological interpretations.

Analyze this dream through a Jungian lens:

---
{dream_text}
---

Provide analysis in the following JSON format:
{{
    "symbols": [
        {{
            "symbol": "specific element from dream",
            "meaning": "Jungian interpretation",
            "archetype": "related archetype if any"
        }}
    ],
    "archetypes": ["list of Jungian archetypes present"],
    "themes": ["psychological themes in the dream"],
    "emotional_tone": "overall emotional quality",
    "interpretation": "detailed interpretation (2-3 paragraphs)",
    "personal_message": "what the unconscious might be communicating",
    "questions_to_consider": ["reflective questions for the dreamer"]
}}

Consider:
- Universal symbols vs. personal symbols
- The dreamer's relationship to figures in the dream
- Compensatory function (what conscious attitude the dream might balance)
- Integration opportunities (what aspects of self seek recognition)
- Shadow elements (repressed or denied aspects)
- Transformation symbols (death, rebirth, crossing thresholds)

{cosmic_context}

Be insightful but not prescriptive. Offer possibilities, not certainties.
Dreams are highly personal - provide a framework for self-exploration."""


COSMIC_CONTEXT_TEMPLATE = """
Current cosmic conditions that may influence dream content:
- Moon Phase: {moon_phase}
- Geomagnetic Activity: {kp_level}
- Mercury Retrograde: {mercury_rx}

Consider how these might manifest symbolically in the dream."""


async def analyze_dream(
    dream_text: str,
    user_context: Optional[dict] = None,
    sensitivity_data: Optional[dict] = None
) -> DreamAnalysis:
    """Analyze a dream using Jungian interpretation via LLM."""

    # Build cosmic context if available
    cosmic_context = ""
    cosmic_correlation = None

    if sensitivity_data:
        astro = sensitivity_data.get("astrology")
        geo = sensitivity_data.get("geomagnetic")

        if astro or geo:
            cosmic_context = COSMIC_CONTEXT_TEMPLATE.format(
                moon_phase=astro.moon_phase.phase_name if astro else "Unknown",
                kp_level=geo.level if geo else "Unknown",
                mercury_rx="Yes" if astro and astro.mercury_retrograde else "No"
            )

            # Generate correlation note
            correlations = []
            if astro:
                if astro.moon_phase.phase_name == "Full Moon":
                    correlations.append("Full Moon often intensifies dream vividness and emotional content")
                if astro.mercury_retrograde:
                    correlations.append("Mercury retrograde may bring dreams of past events or communication themes")
            if geo and geo.kp_index >= 5:
                correlations.append("Geomagnetic storm activity can intensify dream experiences")

            if correlations:
                cosmic_correlation = " ".join(correlations)

    # Prepare prompt
    prompt = DREAM_ANALYSIS_PROMPT.format(
        dream_text=dream_text,
        cosmic_context=cosmic_context
    )

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        response = model.generate_content(prompt, request_options={"timeout": 30})
        text = response.text

        # Parse JSON from response
        import json
        import re

        # Extract JSON from markdown code block if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                text = json_match.group(0)

        data = json.loads(text)

        return DreamAnalysis(
            dream_text=dream_text,
            symbols=data.get("symbols", []),
            archetypes=data.get("archetypes", []),
            themes=data.get("themes", []),
            emotional_tone=data.get("emotional_tone", "reflective"),
            interpretation=data.get("interpretation", ""),
            personal_message=data.get("personal_message", ""),
            questions_to_consider=data.get("questions_to_consider", []),
            cosmic_correlation=cosmic_correlation
        )

    except Exception:
        logger.exception("Error analyzing dream")
        # Return basic analysis on error
        return DreamAnalysis(
            dream_text=dream_text,
            symbols=[],
            archetypes=[],
            themes=["Unknown"],
            emotional_tone="reflective",
            interpretation="Unable to complete analysis. Please try again.",
            personal_message="",
            questions_to_consider=["What emotions did this dream evoke?"],
            cosmic_correlation=cosmic_correlation
        )


async def get_dream_symbols_quick(dream_text: str) -> list[dict]:
    """Quick symbol extraction without full analysis."""
    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        prompt = f"""Extract key symbols from this dream and provide Jungian meanings.
Return as JSON array: [{{"symbol": "...", "meaning": "..."}}]

Dream: {dream_text[:500]}"""

        response = model.generate_content(prompt, request_options={"timeout": 20})
        text = response.text

        import json
        import re

        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            return json.loads(json_match.group(0))
        return []

    except Exception:
        logger.exception("Error extracting dream symbols")
        return []


# Common dream symbols reference (for quick local lookup)
COMMON_SYMBOLS = {
    "water": {
        "meaning": "Emotions, the unconscious, purification",
        "variations": {
            "ocean": "Vast unconscious, collective",
            "river": "Flow of life, transitions",
            "rain": "Emotional release, cleansing",
            "flood": "Overwhelming emotions"
        }
    },
    "house": {
        "meaning": "Self, psyche, different aspects of personality",
        "variations": {
            "basement": "Unconscious, shadow",
            "attic": "Higher mind, memories",
            "rooms": "Different aspects of self"
        }
    },
    "flying": {
        "meaning": "Freedom, transcendence, perspective",
        "variations": {
            "falling": "Loss of control, anxiety",
            "soaring": "Liberation, achievement"
        }
    },
    "death": {
        "meaning": "Transformation, endings, rebirth",
        "note": "Rarely literal - usually symbolic of change"
    },
    "teeth": {
        "meaning": "Power, confidence, self-image",
        "variations": {
            "falling out": "Anxiety about appearance or aging",
            "crumbling": "Feeling of losing control"
        }
    },
    "chase": {
        "meaning": "Avoidance, running from aspects of self",
        "question": "What are you running from in waking life?"
    },
    "snake": {
        "meaning": "Transformation, healing, kundalini, shadow",
        "archetype": "Often represents the shadow or repressed instincts"
    },
    "baby": {
        "meaning": "New beginnings, potential, vulnerability",
        "archetype": "Divine Child archetype"
    },
    "mirror": {
        "meaning": "Self-reflection, truth, persona vs. true self"
    },
    "animals": {
        "meaning": "Instincts, nature, specific qualities of the animal",
        "note": "Consider the animal's characteristics"
    }
}


def get_symbol_reference(symbol: str) -> Optional[dict]:
    """Look up common symbol meaning."""
    symbol_lower = symbol.lower()
    return COMMON_SYMBOLS.get(symbol_lower)


async def track_dream_patterns(
    dreams: list[DreamAnalysis]
) -> dict:
    """Analyze patterns across multiple dreams."""
    if not dreams:
        return {}

    # Aggregate symbols
    all_symbols = {}
    for dream in dreams:
        for sym in dream.symbols:
            name = sym.get("symbol", "").lower()
            if name:
                all_symbols[name] = all_symbols.get(name, 0) + 1

    # Aggregate archetypes
    all_archetypes = {}
    for dream in dreams:
        for arch in dream.archetypes:
            all_archetypes[arch] = all_archetypes.get(arch, 0) + 1

    # Aggregate themes
    all_themes = {}
    for dream in dreams:
        for theme in dream.themes:
            all_themes[theme] = all_themes.get(theme, 0) + 1

    return {
        "recurring_symbols": sorted(all_symbols.items(), key=lambda x: -x[1])[:10],
        "recurring_archetypes": sorted(all_archetypes.items(), key=lambda x: -x[1])[:5],
        "recurring_themes": sorted(all_themes.items(), key=lambda x: -x[1])[:5],
        "dream_count": len(dreams),
        "insight": _generate_pattern_insight(all_symbols, all_archetypes, all_themes)
    }


def _generate_pattern_insight(symbols: dict, archetypes: dict, themes: dict) -> str:
    """Generate insight from patterns."""
    insights = []

    # Check for shadow work indicators
    shadow_keywords = ["chase", "monster", "dark", "hidden", "enemy"]
    shadow_count = sum(symbols.get(k, 0) for k in shadow_keywords)
    if shadow_count > 2:
        insights.append("Recurring shadow themes suggest unconscious material seeking integration")

    # Check for transformation indicators
    transform_keywords = ["death", "snake", "butterfly", "bridge", "door"]
    transform_count = sum(symbols.get(k, 0) for k in transform_keywords)
    if transform_count > 2:
        insights.append("Transformation symbols indicate a period of psychological change")

    if not insights:
        insights.append("Continue dream journaling to reveal deeper patterns")

    return " ".join(insights)
