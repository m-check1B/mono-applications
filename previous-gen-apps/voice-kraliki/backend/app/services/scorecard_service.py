"""Scorecard service for auto-grading agent performance."""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.scorecard import (
    AccuracyDetail,
    EmpathyDetail,
    HandlingDetail,
    ScorecardRequest,
    ScorecardResponse,
)
from app.services.ai_insights import AIInsightsService


class ScorecardService:
    """Generate scorecards from call transcripts."""

    def __init__(self) -> None:
        self._insights = AIInsightsService()
        self._empathy_phrases = [
            "i understand",
            "i'm sorry",
            "i am sorry",
            "i apologize",
            "thanks for your patience",
            "i appreciate",
            "that sounds frustrating",
            "i can imagine",
            "i hear you",
            "thank you for letting us know",
        ]
        self._resolution_phrases = [
            "resolved",
            "refund",
            "replace",
            "escalate",
            "ticket",
            "case",
            "follow up",
            "follow-up",
            "next steps",
            "reset",
            "troubleshoot",
            "schedule",
            "callback",
            "credit",
        ]
        self._follow_up_phrases = [
            "follow up",
            "follow-up",
            "call you back",
            "email you",
            "send you",
            "update you",
            "check in",
        ]

    async def generate_scorecard(self, request: ScorecardRequest) -> ScorecardResponse:
        """Generate a scorecard report from transcripts."""
        agent_text = request.agent_transcript.strip()
        customer_text = (request.customer_transcript or "").strip()
        lower_agent_text = agent_text.lower()

        empathy_detail = await self._score_empathy(agent_text, lower_agent_text)
        accuracy_detail = self._score_accuracy(
            lower_agent_text,
            request.expected_facts,
            request.forbidden_facts,
        )
        handling_detail = self._score_handling(lower_agent_text, customer_text)

        overall_score = round(
            (empathy_detail.score + accuracy_detail.score + handling_detail.score) / 3,
            2,
        )

        summary = self._summarize_overall(overall_score, handling_detail.score)
        highlights, improvements = self._build_feedback(
            empathy_detail,
            accuracy_detail,
            handling_detail,
        )

        return ScorecardResponse(
            overall_score=overall_score,
            summary=summary,
            highlights=highlights,
            improvements=improvements,
            empathy=empathy_detail,
            accuracy=accuracy_detail,
            handling=handling_detail,
            generated_at=datetime.now(UTC),
        )

    async def _score_empathy(self, agent_text: str, lower_agent_text: str) -> EmpathyDetail:
        notes: list[str] = []
        if not agent_text:
            return EmpathyDetail(
                score=0.0,
                sentiment_score=0.0,
                empathy_phrases=[],
                notes=["No agent transcript provided."],
            )

        sentiment = await self._insights.analyze_sentiment(agent_text)
        matched_phrases = [
            phrase for phrase in self._empathy_phrases if phrase in lower_agent_text
        ]

        sentiment_points = 50 + (sentiment.score * 30)
        phrase_bonus = min(20.0, 5.0 * len(matched_phrases))
        score = max(0.0, min(100.0, sentiment_points + phrase_bonus))

        if sentiment.score > 0.2:
            notes.append("Positive agent tone detected.")
        elif sentiment.score < -0.2:
            notes.append("Agent tone feels tense or negative.")
        else:
            notes.append("Neutral tone; consider warmer acknowledgment.")

        if matched_phrases:
            notes.append("Empathy phrases were used in the conversation.")
        else:
            notes.append("No explicit empathy phrases detected.")

        return EmpathyDetail(
            score=round(score, 2),
            sentiment_score=round(sentiment.score, 2),
            empathy_phrases=matched_phrases,
            notes=notes,
        )

    def _score_accuracy(
        self,
        lower_agent_text: str,
        expected_facts: list[str],
        forbidden_facts: list[str],
    ) -> AccuracyDetail:
        notes: list[str] = []
        matched = [fact for fact in expected_facts if fact.lower() in lower_agent_text]
        missing = [fact for fact in expected_facts if fact.lower() not in lower_agent_text]
        flagged = [fact for fact in forbidden_facts if fact.lower() in lower_agent_text]

        if expected_facts:
            coverage = len(matched) / len(expected_facts)
            base_score = coverage * 100
            notes.append(f"Matched {len(matched)} of {len(expected_facts)} required facts.")
        else:
            coverage = 0.0
            base_score = 50.0
            notes.append("No expected facts provided; accuracy set to neutral baseline.")

        penalty = 15.0 * len(flagged)
        score = max(0.0, min(100.0, base_score - penalty))

        if flagged:
            notes.append("Detected statements flagged as incorrect or disallowed.")

        return AccuracyDetail(
            score=round(score, 2),
            matched_facts=matched,
            missing_facts=missing,
            flagged_facts=flagged,
            coverage=round(coverage, 2),
            notes=notes,
        )

    def _score_handling(self, lower_agent_text: str, customer_text: str) -> HandlingDetail:
        notes: list[str] = []
        resolution_signals = [
            phrase for phrase in self._resolution_phrases if phrase in lower_agent_text
        ]
        follow_up_signals = [
            phrase for phrase in self._follow_up_phrases if phrase in lower_agent_text
        ]

        base_score = 40.0
        resolution_bonus = 12.0 * len(resolution_signals)
        follow_up_bonus = 6.0 * len(follow_up_signals)
        question_bonus = 6.0 if "?" in customer_text or "?" in lower_agent_text else 0.0
        score = max(0.0, min(100.0, base_score + resolution_bonus + follow_up_bonus + question_bonus))

        if resolution_signals:
            notes.append("Resolution steps or actions were mentioned.")
        else:
            notes.append("No clear resolution steps detected.")

        if follow_up_signals:
            notes.append("Follow-up commitment detected.")
        else:
            notes.append("No follow-up commitment detected.")

        if question_bonus:
            notes.append("Clarifying question(s) detected.")

        return HandlingDetail(
            score=round(score, 2),
            resolution_signals=resolution_signals,
            follow_up_signals=follow_up_signals,
            notes=notes,
        )

    def _summarize_overall(self, overall_score: float, handling_score: float) -> str:
        if overall_score >= 85:
            return "Excellent performance with strong customer care."
        if overall_score >= 70:
            return "Good performance with room for minor improvements."
        if overall_score >= 55:
            return "Needs improvement in key areas of the call."
        if handling_score < 50:
            return "Critical: resolution steps are unclear or missing."
        return "Critical: performance below expected standards."

    def _build_feedback(
        self,
        empathy: EmpathyDetail,
        accuracy: AccuracyDetail,
        handling: HandlingDetail,
    ) -> tuple[list[str], list[str]]:
        highlights: list[str] = []
        improvements: list[str] = []

        if empathy.score >= 80:
            highlights.append("Strong empathy and supportive tone throughout the call.")
        elif empathy.score < 65:
            improvements.append("Use explicit empathy phrases to acknowledge the customer.")

        if accuracy.score >= 85:
            highlights.append("Key facts were communicated accurately.")
        elif accuracy.score < 70:
            improvements.append("Ensure all required facts are stated clearly.")

        if handling.score >= 80:
            highlights.append("Clear resolution steps and follow-up actions were provided.")
        elif handling.score < 70:
            improvements.append("Clarify next steps and confirm resolution actions.")

        if not highlights:
            highlights.append("Call handled with baseline performance.")

        return highlights, improvements
