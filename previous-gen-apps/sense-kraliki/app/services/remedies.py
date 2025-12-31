"""Holistic remedies matcher.

Provides personalized recommendations for:
- Aromatherapy (essential oils)
- Sound frequencies (healing tones)
- Herbal suggestions
- Grounding techniques
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Remedy:
    """A single remedy recommendation."""
    category: str  # aromatherapy, sound, herbal, technique
    name: str
    description: str
    how_to_use: str
    caution: Optional[str] = None


# Aromatherapy database
AROMATHERAPY = {
    "grounding": [
        Remedy(
            category="aromatherapy",
            name="Vetiver",
            description="Deep, earthy oil for stability and grounding",
            how_to_use="Diffuse 3-4 drops or apply diluted to feet",
            caution="Use carrier oil for skin application"
        ),
        Remedy(
            category="aromatherapy",
            name="Cedarwood",
            description="Warm, woodsy scent for emotional balance",
            how_to_use="Diffuse or add to bath",
        ),
        Remedy(
            category="aromatherapy",
            name="Patchouli",
            description="Rich, earthy aroma for centering",
            how_to_use="Inhale from bottle or diffuse",
        ),
    ],
    "calming": [
        Remedy(
            category="aromatherapy",
            name="Lavender",
            description="Classic calming oil for anxiety and sleep",
            how_to_use="Diffuse, pillow spray, or diluted skin application",
        ),
        Remedy(
            category="aromatherapy",
            name="Chamomile (Roman)",
            description="Gentle, soothing for nervous tension",
            how_to_use="Diffuse or add to warm bath",
        ),
        Remedy(
            category="aromatherapy",
            name="Bergamot",
            description="Citrus with calming properties, uplifting",
            how_to_use="Diffuse or inhale directly",
            caution="Photosensitive - avoid sun after skin application"
        ),
    ],
    "energizing": [
        Remedy(
            category="aromatherapy",
            name="Peppermint",
            description="Invigorating, clears mental fog",
            how_to_use="Inhale directly or apply diluted to temples",
            caution="Avoid near eyes, may irritate sensitive skin"
        ),
        Remedy(
            category="aromatherapy",
            name="Rosemary",
            description="Stimulating, supports focus and memory",
            how_to_use="Diffuse during work or study",
            caution="Avoid if epileptic or pregnant"
        ),
        Remedy(
            category="aromatherapy",
            name="Lemon",
            description="Fresh, uplifting, mood brightener",
            how_to_use="Diffuse or add to cleaning",
            caution="Photosensitive"
        ),
    ],
    "protective": [
        Remedy(
            category="aromatherapy",
            name="Frankincense",
            description="Sacred oil for spiritual protection and meditation",
            how_to_use="Diffuse during meditation or apply to third eye",
        ),
        Remedy(
            category="aromatherapy",
            name="Sage (Clary)",
            description="Cleansing, helps release negative energy",
            how_to_use="Diffuse for space clearing",
        ),
    ],
}

# Sound frequencies database
SOUND_FREQUENCIES = {
    "healing": [
        Remedy(
            category="sound",
            name="528 Hz - Love Frequency",
            description="DNA repair, transformation, miracles",
            how_to_use="Listen for 15-30 min, preferably with headphones",
        ),
        Remedy(
            category="sound",
            name="432 Hz - Natural Tuning",
            description="Harmony with nature, calming vibration",
            how_to_use="Listen to 432 Hz tuned music during relaxation",
        ),
        Remedy(
            category="sound",
            name="396 Hz - Liberation",
            description="Releases guilt and fear, liberating",
            how_to_use="Listen during emotional processing",
        ),
    ],
    "grounding": [
        Remedy(
            category="sound",
            name="174 Hz - Foundation",
            description="Lowest Solfeggio, grounding and pain relief",
            how_to_use="Listen lying down, feel vibration in body",
        ),
        Remedy(
            category="sound",
            name="285 Hz - Tissue Healing",
            description="Regeneration, influences energy field",
            how_to_use="Listen during rest or sleep",
        ),
    ],
    "clarity": [
        Remedy(
            category="sound",
            name="741 Hz - Expression",
            description="Awakening intuition, solving problems",
            how_to_use="Listen before creative work or decisions",
        ),
        Remedy(
            category="sound",
            name="852 Hz - Intuition",
            description="Returns to spiritual order, inner strength",
            how_to_use="Listen during meditation",
        ),
    ],
    "spiritual": [
        Remedy(
            category="sound",
            name="963 Hz - Divine Connection",
            description="Highest Solfeggio, pineal gland activation",
            how_to_use="Listen during spiritual practice",
        ),
        Remedy(
            category="sound",
            name="7.83 Hz - Schumann",
            description="Earth's natural frequency, deep grounding",
            how_to_use="Binaural beats or embedded in music",
        ),
    ],
}

# Herbal suggestions (general wellness, not medical advice)
HERBAL_SUGGESTIONS = {
    "calming": [
        Remedy(
            category="herbal",
            name="Chamomile Tea",
            description="Gentle nervine for relaxation and sleep",
            how_to_use="Brew 1-2 tsp dried flowers in hot water, 10 min",
            caution="Avoid if allergic to ragweed/daisies"
        ),
        Remedy(
            category="herbal",
            name="Passionflower",
            description="Calming herb for anxiety and overthinking",
            how_to_use="Tea or tincture before bed",
            caution="May cause drowsiness"
        ),
        Remedy(
            category="herbal",
            name="Lemon Balm",
            description="Mint family herb for nervous tension",
            how_to_use="Fresh or dried tea, can be grown at home",
        ),
    ],
    "energizing": [
        Remedy(
            category="herbal",
            name="Ginseng",
            description="Adaptogen for energy and vitality",
            how_to_use="Tea or supplement in morning",
            caution="Avoid with blood pressure issues"
        ),
        Remedy(
            category="herbal",
            name="Green Tea",
            description="Gentle caffeine with L-theanine for focus",
            how_to_use="Brew 2-3 min, don't overbrew",
        ),
    ],
    "protective": [
        Remedy(
            category="herbal",
            name="Ashwagandha",
            description="Adaptogen for stress resilience",
            how_to_use="Supplement or powder in warm milk",
            caution="Avoid if thyroid issues, pregnant"
        ),
        Remedy(
            category="herbal",
            name="Holy Basil (Tulsi)",
            description="Sacred adaptogen for overall wellbeing",
            how_to_use="Tea, 1-2 cups daily",
        ),
    ],
    "sleep": [
        Remedy(
            category="herbal",
            name="Valerian Root",
            description="Strong sedative herb for sleep",
            how_to_use="Tea or tincture 30 min before bed",
            caution="May cause vivid dreams, don't mix with sedatives"
        ),
        Remedy(
            category="herbal",
            name="Lavender Tea",
            description="Gentle relaxant for sleep preparation",
            how_to_use="Brew flowers in hot water, drink before bed",
        ),
    ],
}

# Grounding techniques
TECHNIQUES = {
    "quick": [
        Remedy(
            category="technique",
            name="5-4-3-2-1 Grounding",
            description="Sensory awareness technique",
            how_to_use="Name 5 things you see, 4 hear, 3 feel, 2 smell, 1 taste",
        ),
        Remedy(
            category="technique",
            name="Cold Water",
            description="Quick reset for overwhelm",
            how_to_use="Splash cold water on face or hold ice cube",
        ),
        Remedy(
            category="technique",
            name="Deep Breathing",
            description="4-7-8 breathing for immediate calm",
            how_to_use="Inhale 4 sec, hold 7, exhale 8. Repeat 3-4 times",
        ),
    ],
    "physical": [
        Remedy(
            category="technique",
            name="Earthing/Grounding",
            description="Direct contact with earth",
            how_to_use="Walk barefoot on grass/sand for 15+ min",
        ),
        Remedy(
            category="technique",
            name="Body Scan",
            description="Progressive awareness of physical sensations",
            how_to_use="Lie down, slowly notice each body part from toes up",
        ),
    ],
    "energy": [
        Remedy(
            category="technique",
            name="Energy Shielding",
            description="Visualization for empaths",
            how_to_use="Visualize white/golden light surrounding your body as protection",
        ),
        Remedy(
            category="technique",
            name="Salt Bath",
            description="Energy cleansing through salt water",
            how_to_use="Add 1 cup Epsom or sea salt to warm bath, soak 20 min",
        ),
    ],
}


@dataclass
class RemedyPlan:
    """Personalized remedy recommendations."""
    aromatherapy: list[Remedy]
    sound: list[Remedy]
    herbal: list[Remedy]
    techniques: list[Remedy]
    focus_area: str  # What these remedies target

    def to_summary(self) -> str:
        """Generate readable summary."""
        lines = [f"Remedy Plan - Focus: {self.focus_area}", ""]

        if self.aromatherapy:
            lines.append("Essential Oils:")
            for r in self.aromatherapy:
                lines.append(f"  - {r.name}: {r.description}")

        if self.sound:
            lines.append("\nHealing Frequencies:")
            for r in self.sound:
                lines.append(f"  - {r.name}: {r.description}")

        if self.herbal:
            lines.append("\nHerbal Support:")
            for r in self.herbal:
                caution = f" ({r.caution})" if r.caution else ""
                lines.append(f"  - {r.name}: {r.description}{caution}")

        if self.techniques:
            lines.append("\nTechniques:")
            for r in self.techniques:
                lines.append(f"  - {r.name}: {r.how_to_use}")

        return "\n".join(lines)


def get_remedies_for_sensitivity(
    sensitivity_level: str,
    primary_factors: list[str] = None
) -> RemedyPlan:
    """Get remedies based on sensitivity level and contributing factors."""

    # Determine focus based on level and factors
    if sensitivity_level in ["high", "extreme"]:
        focus = "protective"
        aroma_key = "protective"
        sound_key = "grounding"
        herb_key = "calming"
        tech_key = "quick"
    elif sensitivity_level == "elevated":
        focus = "calming"
        aroma_key = "calming"
        sound_key = "healing"
        herb_key = "calming"
        tech_key = "physical"
    elif sensitivity_level == "moderate":
        focus = "balance"
        aroma_key = "grounding"
        sound_key = "healing"
        herb_key = "protective"
        tech_key = "energy"
    else:  # low
        focus = "enhancement"
        aroma_key = "energizing"
        sound_key = "clarity"
        herb_key = "energizing"
        tech_key = "physical"

    # Adjust based on specific factors
    if primary_factors:
        if "geomagnetic" in primary_factors or "solar" in primary_factors:
            aroma_key = "grounding"
            sound_key = "grounding"

        if "weather" in primary_factors:
            herb_key = "calming"

        if "emotional" in primary_factors:
            sound_key = "healing"
            herb_key = "calming"

    return RemedyPlan(
        aromatherapy=AROMATHERAPY.get(aroma_key, [])[:2],
        sound=SOUND_FREQUENCIES.get(sound_key, [])[:2],
        herbal=HERBAL_SUGGESTIONS.get(herb_key, [])[:2],
        techniques=TECHNIQUES.get(tech_key, [])[:2],
        focus_area=focus
    )


def get_sleep_remedies() -> RemedyPlan:
    """Get remedies specifically for sleep support."""
    return RemedyPlan(
        aromatherapy=AROMATHERAPY["calming"][:2],
        sound=[
            SOUND_FREQUENCIES["grounding"][0],  # 174 Hz
            SOUND_FREQUENCIES["spiritual"][1],  # Schumann
        ],
        herbal=HERBAL_SUGGESTIONS["sleep"],
        techniques=[
            TECHNIQUES["physical"][1],  # Body scan
            TECHNIQUES["quick"][2],  # Deep breathing
        ],
        focus_area="sleep"
    )


def get_focus_remedies() -> RemedyPlan:
    """Get remedies for mental clarity and focus."""
    return RemedyPlan(
        aromatherapy=AROMATHERAPY["energizing"][:2],
        sound=SOUND_FREQUENCIES["clarity"],
        herbal=HERBAL_SUGGESTIONS["energizing"],
        techniques=[TECHNIQUES["quick"][2]],  # Breathing
        focus_area="focus"
    )


def get_emotional_remedies() -> RemedyPlan:
    """Get remedies for emotional overwhelm."""
    return RemedyPlan(
        aromatherapy=[
            AROMATHERAPY["calming"][0],  # Lavender
            AROMATHERAPY["protective"][0],  # Frankincense
        ],
        sound=SOUND_FREQUENCIES["healing"][:2],
        herbal=[
            HERBAL_SUGGESTIONS["calming"][0],  # Chamomile
            HERBAL_SUGGESTIONS["calming"][1],  # Passionflower
        ],
        techniques=[
            TECHNIQUES["quick"][0],  # 5-4-3-2-1
            TECHNIQUES["energy"][0],  # Shielding
        ],
        focus_area="emotional"
    )
