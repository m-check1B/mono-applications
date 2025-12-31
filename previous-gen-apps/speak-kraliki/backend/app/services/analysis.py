"""
Speak by Kraliki - Analysis Service
Sentiment analysis, topic extraction, and alert generation
"""

import re
from decimal import Decimal
from datetime import datetime

# Alert trigger keywords (Czech)
ALERT_TRIGGERS = {
    "flight_risk": {
        "keywords": ["odejit", "hledam praci", "nabidka", "konec", "vypovet", "uvazuji o zmene"],
        "severity": "high",
        "description": "Zamestnanec mozna uvazuje o odchodu"
    },
    "burnout": {
        "keywords": ["vyhoreni", "nestíham", "unaveny", "vycerpany", "presčas", "nonstop", "uz nemuzů"],
        "severity": "high",
        "description": "Znamky vyhoreni nebo pretizeni"
    },
    "toxic_manager": {
        "keywords": ["sef je", "manazer je", "vedouci je", "nefer", "sikana", "ponizovani"],
        "severity": "high",
        "description": "Negativni zpetna vazba na management"
    },
    "team_conflict": {
        "keywords": ["konflikt", "hadka", "nespokojen s kolegy", "spatna atmosfera", "napeti"],
        "severity": "medium",
        "description": "Konflikt v tymu"
    },
    "low_engagement": {
        "keywords": ["nezajima me", "nuda", "rutina", "nic me nebavi", "demotivovany"],
        "severity": "medium",
        "description": "Nizke zapojeni a motivace"
    },
}

# Topic categories
TOPIC_KEYWORDS = {
    "workload": ["prace", "ukoly", "deadline", "projekt", "vytizeni", "prescasy"],
    "management": ["sef", "manazer", "vedouci", "vedeni", "rozhodnuti"],
    "team": ["tym", "kolega", "kolegove", "spoluprace", "komunikace"],
    "growth": ["rust", "rozvoj", "skoleni", "kariéra", "povyseni", "uceni"],
    "compensation": ["plat", "mzda", "odmena", "benefity", "penize"],
    "work_life_balance": ["rovnovaha", "rodina", "volno", "dovolena", "flexibilita"],
    "culture": ["kultura", "atmosfera", "hodnoty", "firma", "prostredi"],
    "tools": ["nastroje", "systemy", "software", "vybaveni", "procesy"],
}


class AnalysisService:
    """Service for analyzing conversation transcripts."""

    def analyze_transcript(self, transcript: list[dict]) -> dict:
        """
        Analyze full conversation transcript.
        Returns sentiment, topics, flags, and summary.
        """
        # Extract all user messages
        user_messages = [
            turn["content"]
            for turn in transcript
            if turn.get("role") == "user"
        ]
        full_text = " ".join(user_messages).lower()

        # Analyze
        sentiment = self._calculate_sentiment(full_text)
        topics = self._extract_topics(full_text)
        flags = self._detect_alerts(full_text)
        summary = self._generate_summary(user_messages, topics, sentiment)

        return {
            "sentiment_score": sentiment,
            "topics": topics,
            "flags": flags,
            "summary": summary,
        }

    def _calculate_sentiment(self, text: str) -> Decimal:
        """
        Calculate sentiment score from -1.0 (negative) to 1.0 (positive).
        Uses simple keyword-based approach (replace with ML in production).
        """
        positive_words = [
            "spokojeny", "dobre", "vyborne", "super", "skvele", "rad", "motivovany",
            "tesi", "uzasne", "pozitivni", "podporuje", "pomaha", "libi"
        ]
        negative_words = [
            "spatne", "hrozne", "frustruje", "trapi", "nespokojeny", "problem",
            "tezke", "unaveny", "stresovany", "zly", "nefer", "konflikt", "nemuzů"
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        total = positive_count + negative_count
        if total == 0:
            return Decimal("0.00")

        score = (positive_count - negative_count) / max(total, 1)
        # Clamp to -1.0 to 1.0
        score = max(-1.0, min(1.0, score))
        return Decimal(str(round(score, 2)))

    def _extract_topics(self, text: str) -> list[str]:
        """Extract discussed topics from text."""
        topics = []
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        return topics[:5]  # Max 5 topics

    def _detect_alerts(self, text: str) -> list[str]:
        """Detect alert-worthy content in text."""
        alerts = []
        for alert_type, config in ALERT_TRIGGERS.items():
            if any(keyword in text for keyword in config["keywords"]):
                alerts.append(alert_type)
        return alerts

    def _generate_summary(
        self,
        messages: list[str],
        topics: list[str],
        sentiment: Decimal
    ) -> str:
        """Generate brief summary of conversation."""
        # Simple template-based summary (replace with AI in production)
        sentiment_label = "pozitivni" if sentiment > 0.2 else "negativni" if sentiment < -0.2 else "neutralni"
        topic_str = ", ".join(topics[:3]) if topics else "obecne tema"

        if len(messages) < 2:
            return "Kratky rozhovor bez podrobnosti."

        return f"Zamestnanec vyjadril {sentiment_label} nazor. Hlavni temata: {topic_str}."

    def generate_alerts(
        self,
        conversation_id: str,
        company_id: str,
        department_id: str | None,
        flags: list[str],
        transcript: list[dict]
    ) -> list[dict]:
        """Generate alert objects from detected flags."""
        alerts = []
        full_text = " ".join(
            turn["content"] for turn in transcript if turn.get("role") == "user"
        ).lower()

        for flag in flags:
            if flag not in ALERT_TRIGGERS:
                continue

            config = ALERT_TRIGGERS[flag]
            # Find triggering keywords for transparency
            triggers = [kw for kw in config["keywords"] if kw in full_text]

            alerts.append({
                "type": flag,
                "severity": config["severity"],
                "description": config["description"],
                "trigger_keywords": ", ".join(triggers[:3]),
                "conversation_id": conversation_id,
                "company_id": company_id,
                "department_id": department_id,
            })

        return alerts

    def calculate_department_sentiment(
        self,
        conversations: list[dict]
    ) -> dict:
        """Calculate aggregated sentiment for department."""
        if not conversations:
            return {
                "average": Decimal("0.00"),
                "count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            }

        sentiments = [
            float(c["sentiment_score"])
            for c in conversations
            if c.get("sentiment_score") is not None
        ]

        if not sentiments:
            return {
                "average": Decimal("0.00"),
                "count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            }

        avg = sum(sentiments) / len(sentiments)

        return {
            "average": Decimal(str(round(avg, 2))),
            "count": len(sentiments),
            "positive_count": sum(1 for s in sentiments if s > 0.2),
            "negative_count": sum(1 for s in sentiments if s < -0.2),
            "neutral_count": sum(1 for s in sentiments if -0.2 <= s <= 0.2),
        }
