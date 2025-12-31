"""Biorhythm calculator using classic 4-cycle theory.

Cycles:
- Physical: 23 days
- Emotional: 28 days
- Intellectual: 33 days
- Intuitive: 38 days
"""
from datetime import UTC, datetime, timedelta
from dataclasses import dataclass
import math


@dataclass
class BiorhythmData:
    """Current biorhythm values."""
    physical: int  # -100 to +100
    emotional: int
    intellectual: int
    intuitive: int
    birth_date: datetime
    calc_date: datetime

    @property
    def physical_phase(self) -> str:
        return self._phase(self.physical)

    @property
    def emotional_phase(self) -> str:
        return self._phase(self.emotional)

    @property
    def intellectual_phase(self) -> str:
        return self._phase(self.intellectual)

    @property
    def intuitive_phase(self) -> str:
        return self._phase(self.intuitive)

    def _phase(self, value: int) -> str:
        if abs(value) < 10:
            return "critical"
        elif value > 50:
            return "high"
        elif value > 0:
            return "rising"
        elif value > -50:
            return "falling"
        return "low"

    @property
    def critical_days(self) -> list[str]:
        """List cycles that are in critical phase (crossing zero)."""
        critical = []
        if abs(self.physical) < 10:
            critical.append("physical")
        if abs(self.emotional) < 10:
            critical.append("emotional")
        if abs(self.intellectual) < 10:
            critical.append("intellectual")
        if abs(self.intuitive) < 10:
            critical.append("intuitive")
        return critical

    @property
    def sensitivity_score(self) -> int:
        """Biorhythm contribution to sensitivity (0-20).

        Low values in any cycle increase sensitivity.
        Critical days (crossing zero) are most impactful.
        """
        score = 0

        # Critical days are most impactful
        score += len(self.critical_days) * 5

        # Low values increase sensitivity
        for value in [self.physical, self.emotional, self.intellectual, self.intuitive]:
            if value < -50:
                score += 2
            elif value < 0:
                score += 1

        return min(20, score)

    @property
    def overall(self) -> int:
        """Overall biorhythm average (-100 to +100)."""
        return int((self.physical + self.emotional + self.intellectual + self.intuitive) / 4)

    @property
    def interpretation(self) -> str:
        """Human-readable interpretation."""
        if self.overall > 50:
            return "Peak performance period - excellent for challenging tasks"
        elif self.overall > 20:
            return "Good energy levels - productive period"
        elif self.overall > -20:
            return "Balanced state - normal functioning"
        elif self.overall > -50:
            return "Low energy period - avoid overexertion"
        return "Recovery period - rest and self-care recommended"


def calculate_cycle(days_lived: int, cycle_length: int) -> int:
    """Calculate biorhythm value for a cycle.

    Returns value from -100 to +100.
    """
    position = days_lived % cycle_length
    radians = (2 * math.pi * position) / cycle_length
    return int(math.sin(radians) * 100)


def calculate_biorhythm(birth_date: datetime, calc_date: datetime = None) -> BiorhythmData:
    """Calculate biorhythm for given birth date."""
    if calc_date is None:
        calc_date = datetime.now(UTC)

    # Calculate days lived
    delta = calc_date - birth_date
    days_lived = delta.days

    return BiorhythmData(
        physical=calculate_cycle(days_lived, 23),
        emotional=calculate_cycle(days_lived, 28),
        intellectual=calculate_cycle(days_lived, 33),
        intuitive=calculate_cycle(days_lived, 38),
        birth_date=birth_date,
        calc_date=calc_date
    )


def get_biorhythm_forecast(
    birth_date: datetime,
    days: int = 30
) -> list[dict]:
    """Generate biorhythm forecast for next N days."""
    forecasts = []
    today = datetime.now(UTC)

    for day_offset in range(days):
        forecast_date = today + timedelta(days=day_offset)
        bio = calculate_biorhythm(birth_date, forecast_date)

        forecasts.append({
            "date": forecast_date.strftime("%Y-%m-%d"),
            "physical": bio.physical,
            "emotional": bio.emotional,
            "intellectual": bio.intellectual,
            "intuitive": bio.intuitive,
            "overall": bio.overall,
            "critical_days": bio.critical_days,
            "interpretation": bio.interpretation
        })

    return forecasts


def find_next_critical_days(
    birth_date: datetime,
    search_days: int = 30
) -> list[dict]:
    """Find upcoming critical days (cycle crossings)."""
    critical_events = []
    today = datetime.now(UTC)

    for day_offset in range(search_days):
        forecast_date = today + timedelta(days=day_offset)
        bio = calculate_biorhythm(birth_date, forecast_date)

        if bio.critical_days:
            critical_events.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "days_from_now": day_offset,
                "cycles": bio.critical_days,
                "advice": _get_critical_day_advice(bio.critical_days)
            })

    return critical_events


def _get_critical_day_advice(critical_cycles: list[str]) -> str:
    """Generate advice for critical days."""
    advice_map = {
        "physical": "Avoid strenuous activities, risk of accidents higher",
        "emotional": "Emotional instability - be patient with yourself and others",
        "intellectual": "Mental fog possible - double-check important decisions",
        "intuitive": "Trust gut feelings less today - seek external input"
    }

    if len(critical_cycles) >= 3:
        return "Multiple critical cycles - consider this a rest day"

    return "; ".join(advice_map.get(c, "") for c in critical_cycles)


def get_compatibility(
    birth_date_1: datetime,
    birth_date_2: datetime
) -> dict:
    """Calculate biorhythm compatibility between two people."""
    bio1 = calculate_biorhythm(birth_date_1)
    bio2 = calculate_biorhythm(birth_date_2)

    # Compatibility based on cycle alignment
    def cycle_compatibility(v1: int, v2: int) -> int:
        # Same direction = higher compatibility
        same_direction = (v1 >= 0) == (v2 >= 0)
        magnitude_diff = abs(abs(v1) - abs(v2))

        if same_direction:
            return max(0, 100 - magnitude_diff)
        return max(0, 50 - magnitude_diff // 2)

    return {
        "physical": cycle_compatibility(bio1.physical, bio2.physical),
        "emotional": cycle_compatibility(bio1.emotional, bio2.emotional),
        "intellectual": cycle_compatibility(bio1.intellectual, bio2.intellectual),
        "intuitive": cycle_compatibility(bio1.intuitive, bio2.intuitive),
        "overall": int((
            cycle_compatibility(bio1.physical, bio2.physical) +
            cycle_compatibility(bio1.emotional, bio2.emotional) +
            cycle_compatibility(bio1.intellectual, bio2.intellectual) +
            cycle_compatibility(bio1.intuitive, bio2.intuitive)
        ) / 4)
    }
