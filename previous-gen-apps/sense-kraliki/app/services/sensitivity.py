"""Unified sensitivity score engine.

Combines all 9 data sources into a single 0-100 sensitivity score.
"""
from datetime import UTC, datetime
from dataclasses import dataclass, field
from typing import Optional
import asyncio

from app.data.noaa import get_noaa_data, GeomagneticData, SolarFlare
from app.data.usgs import get_earthquake_score, Earthquake
from app.data.weather import WeatherData, fetch_weather
from app.data.schumann import get_schumann_data, SchumannData
from app.data.astro import get_astro_data, AstroData
from app.services.biorhythm import calculate_biorhythm, BiorhythmData


@dataclass
class SensitivityBreakdown:
    """Individual source contributions to total score."""
    geomagnetic: int = 0  # 0-30 (Kp index)
    solar_flares: int = 0  # 0-20
    earthquakes: int = 0  # 0-10
    schumann: int = 0  # 0-20
    weather: int = 0  # 0-15
    astrology: int = 0  # 0-25
    biorhythm: int = 0  # 0-20

    @property
    def total(self) -> int:
        """Total raw score (before normalization)."""
        return (
            self.geomagnetic +
            self.solar_flares +
            self.earthquakes +
            self.schumann +
            self.weather +
            self.astrology +
            self.biorhythm
        )

    @property
    def normalized(self) -> int:
        """Normalized score 0-100."""
        # Max possible: 30+20+10+20+15+25+20 = 140
        max_possible = 140
        return min(100, int(self.total / max_possible * 100))


@dataclass
class SensitivityReport:
    """Complete sensitivity assessment."""
    score: int  # 0-100
    level: str  # low, moderate, elevated, high, extreme
    breakdown: SensitivityBreakdown
    alerts: list[str]
    recommendations: list[str]
    timestamp: datetime

    # Raw data for detailed view
    geomagnetic: Optional[GeomagneticData] = None
    solar_flares: list[SolarFlare] = field(default_factory=list)
    earthquakes: list[Earthquake] = field(default_factory=list)
    schumann: Optional[SchumannData] = None
    weather: Optional[WeatherData] = None
    astrology: Optional[AstroData] = None
    biorhythm: Optional[BiorhythmData] = None

    @property
    def emoji(self) -> str:
        """Level indicator emoji."""
        emojis = {
            "low": "🟢",
            "moderate": "🟡",
            "elevated": "🟠",
            "high": "🔴",
            "extreme": "⚠️"
        }
        return emojis.get(self.level, "⚪")

    def to_summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"{self.emoji} Sensitivity Level: {self.level.upper()} ({self.score}/100)",
            "",
            "📊 Contributing Factors:"
        ]

        # Show significant factors
        factors = [
            ("🌍 Geomagnetic", self.breakdown.geomagnetic, 30),
            ("☀️ Solar", self.breakdown.solar_flares, 20),
            ("🌋 Seismic", self.breakdown.earthquakes, 10),
            ("⚡ Schumann", self.breakdown.schumann, 20),
            ("🌤️ Weather", self.breakdown.weather, 15),
            ("🌙 Astrology", self.breakdown.astrology, 25),
            ("🔄 Biorhythm", self.breakdown.biorhythm, 20),
        ]

        for name, score, max_score in factors:
            if score > 0:
                bar_fill = int(score / max_score * 10)
                bar = "█" * bar_fill + "░" * (10 - bar_fill)
                lines.append(f"  {name}: [{bar}] {score}/{max_score}")

        if self.alerts:
            lines.extend(["", "⚠️ Alerts:"])
            for alert in self.alerts:
                lines.append(f"  • {alert}")

        if self.recommendations:
            lines.extend(["", "💡 Recommendations:"])
            for rec in self.recommendations[:3]:  # Top 3
                lines.append(f"  • {rec}")

        return "\n".join(lines)


def get_level(score: int) -> str:
    """Convert score to level."""
    if score < 20:
        return "low"
    elif score < 40:
        return "moderate"
    elif score < 60:
        return "elevated"
    elif score < 80:
        return "high"
    return "extreme"


def generate_alerts(report: SensitivityReport) -> list[str]:
    """Generate alerts based on data."""
    alerts = []

    # Geomagnetic alerts
    if report.geomagnetic and report.geomagnetic.kp_index >= 5:
        alerts.append(f"Geomagnetic storm active (Kp {report.geomagnetic.kp_index})")

    # Solar flare alerts
    significant_flares = [f for f in report.solar_flares if f.is_significant]
    if significant_flares:
        alerts.append(f"{len(significant_flares)} significant solar flare(s) in last 24h")

    # Earthquake alerts
    major_quakes = [q for q in report.earthquakes if q.is_major]
    if major_quakes:
        alerts.append(f"{len(major_quakes)} major earthquake(s) (M6+) detected")

    # Schumann alerts
    if report.schumann and report.schumann.intensity == "extreme":
        alerts.append("Extreme Schumann resonance activity")

    # Weather alerts
    if report.weather:
        if report.weather.pressure_status in ["dropping_fast", "rising_fast"]:
            alerts.append(f"Rapid pressure change ({report.weather.pressure_change:+.1f} hPa)")

    # Astrology alerts
    if report.astrology:
        if report.astrology.mercury_retrograde:
            alerts.append("Mercury retrograde active")
        if report.astrology.moon_phase.phase_name == "Full Moon":
            alerts.append("Full Moon - heightened emotions")

    # Biorhythm alerts
    if report.biorhythm:
        critical = report.biorhythm.critical_days
        if critical:
            alerts.append(f"Biorhythm critical day(s): {', '.join(critical)}")

    return alerts


def generate_recommendations(report: SensitivityReport) -> list[str]:
    """Generate recommendations based on sensitivity level and factors."""
    recs = []

    # General level-based recommendations
    if report.score >= 60:
        recs.append("Consider reducing stimulants (caffeine, social media)")
        recs.append("Extra rest and grounding activities recommended")

    if report.score >= 80:
        recs.append("Avoid major decisions today if possible")
        recs.append("Gentle exercise like walking or yoga preferred")

    # Factor-specific recommendations
    if report.geomagnetic and report.geomagnetic.kp_index >= 5:
        recs.append("Grounding exercises help during geomagnetic storms")

    if report.weather and report.weather.humidity > 85:
        recs.append("High humidity - stay hydrated, consider indoor activities")

    if report.weather and abs(report.weather.pressure_change) > 10:
        recs.append("Pressure change - headache prevention: hydrate, rest")

    if report.astrology and report.astrology.mercury_retrograde:
        recs.append("Mercury retrograde - double-check communications")

    if report.biorhythm:
        if report.biorhythm.physical < 30:
            recs.append("Physical biorhythm low - prioritize rest over exercise")
        if report.biorhythm.emotional < 30:
            recs.append("Emotional biorhythm low - self-care and boundaries")
        if report.biorhythm.intellectual < 30:
            recs.append("Mental biorhythm low - avoid complex tasks")

    # Ensure we have at least some recommendations
    if not recs:
        recs.append("Conditions favorable - good day for productivity")

    return recs


async def calculate_sensitivity(
    latitude: float = None,
    longitude: float = None,
    birth_date: datetime = None
) -> SensitivityReport:
    """Calculate comprehensive sensitivity score."""

    breakdown = SensitivityBreakdown()
    alerts = []

    # Fetch all data sources concurrently
    tasks = [
        get_noaa_data(),
        get_earthquake_score(),
        get_schumann_data(),
        get_astro_data(),
    ]

    # Weather needs coordinates
    if latitude is not None and longitude is not None:
        tasks.append(fetch_weather(latitude, longitude))
    else:
        tasks.append(asyncio.sleep(0))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    noaa_data = results[0] if not isinstance(results[0], Exception) else {}
    eq_score, earthquakes = results[1] if not isinstance(results[1], Exception) else (0, [])
    schumann = results[2] if not isinstance(results[2], Exception) else None
    astro = results[3] if not isinstance(results[3], Exception) else None
    weather = results[4] if not isinstance(results[4], Exception) else None

    # Extract NOAA components
    geomagnetic = noaa_data.get("geomagnetic") if isinstance(noaa_data, dict) else None
    solar_flares = noaa_data.get("solar_flares", []) if isinstance(noaa_data, dict) else []

    # Calculate biorhythm if birth date provided
    biorhythm = None
    if birth_date:
        biorhythm = calculate_biorhythm(birth_date)

    # Build breakdown
    if geomagnetic:
        breakdown.geomagnetic = geomagnetic.sensitivity_score

    if solar_flares:
        breakdown.solar_flares = sum(f.sensitivity_score for f in solar_flares[:3])

    breakdown.earthquakes = eq_score

    if schumann:
        breakdown.schumann = schumann.sensitivity_score

    if weather:
        breakdown.weather = weather.sensitivity_score

    if astro:
        breakdown.astrology = astro.sensitivity_score

    if biorhythm:
        breakdown.biorhythm = biorhythm.sensitivity_score

    # Create report
    score = breakdown.normalized
    level = get_level(score)

    report = SensitivityReport(
        score=score,
        level=level,
        breakdown=breakdown,
        alerts=[],  # Will be generated
        recommendations=[],  # Will be generated
        timestamp=datetime.now(UTC),
        geomagnetic=geomagnetic,
        solar_flares=solar_flares,
        earthquakes=earthquakes,
        schumann=schumann,
        weather=weather,
        astrology=astro,
        biorhythm=biorhythm
    )

    # Generate alerts and recommendations
    report.alerts = generate_alerts(report)
    report.recommendations = generate_recommendations(report)

    return report


async def get_quick_score() -> tuple[int, str]:
    """Get just the score and level (faster, no detailed breakdown)."""
    report = await calculate_sensitivity()
    return report.score, report.level
