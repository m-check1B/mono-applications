"""Enhanced Scorecard Service using LLMs for automated agent grading."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

import google.generativeai as genai
from openai import AsyncOpenAI

from app.config.settings import get_settings
from app.models.scorecard import (
    AccuracyDetail,
    EmpathyDetail,
    HandlingDetail,
    ScorecardRequest,
    ScorecardResponse,
)

logger = logging.getLogger(__name__)


class EnhancedScorecardService:
    """Generate scorecards using LLM analysis."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.openai_client = None
        self.gemini_client = None

        if self.settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)

        if self.settings.gemini_api_key:
            genai.configure(api_key=self.settings.gemini_api_key)
            self.gemini_client = genai.GenerativeModel("gemini-1.5-flash")

    async def generate_scorecard(self, request: ScorecardRequest) -> ScorecardResponse:
        """Generate a scorecard report using LLM analysis."""
        if not self.openai_client and not self.gemini_client:
            logger.warning("No AI providers configured for scorecard generation, falling back to rule-based service")
            from app.services.scorecard_service import ScorecardService
            return await ScorecardService().generate_scorecard(request)

        prompt = self._build_prompt(request)

        try:
            if self.openai_client:
                result = await self._generate_with_openai(prompt)
            else:
                result = await self._generate_with_gemini(prompt)

            return self._parse_result(result)
        except Exception as e:
            logger.error(f"Failed to generate enhanced scorecard: {e}")
            # Fallback to rule-based service
            from app.services.scorecard_service import ScorecardService
            return await ScorecardService().generate_scorecard(request)

    def _build_prompt(self, request: ScorecardRequest) -> str:
        agent_transcript = request.agent_transcript
        customer_transcript = request.customer_transcript or "N/A"
        expected_facts = ", ".join(request.expected_facts) if request.expected_facts else "None provided"
        forbidden_facts = ", ".join(request.forbidden_facts) if request.forbidden_facts else "None provided"

        return f"""
        Analyze the following call transcript and generate an automated scorecard for the AGENT.
        
        AGENT TRANSCRIPT:
        {agent_transcript}
        
        CUSTOMER TRANSCRIPT:
        {customer_transcript}
        
        EXPECTED FACTS (Agent SHOULD mention these):
        {expected_facts}
        
        FORBIDDEN FACTS (Agent should NOT mention these):
        {forbidden_facts}
        
        Provide a JSON response with the following structure:
        {{
            "overall_score": float (0-100),
            "summary": "1-2 sentence overview",
            "highlights": ["list of positive points"],
            "improvements": ["list of areas for improvement"],
            "empathy": {{
                "score": float (0-100),
                "sentiment_score": float (-1.0 to 1.0),
                "empathy_phrases": ["list of identified empathetic phrases used by agent"],
                "notes": ["specific notes on empathy"]
            }},
            "accuracy": {{
                "score": float (0-100),
                "matched_facts": ["expected facts that were mentioned"],
                "missing_facts": ["expected facts that were NOT mentioned"],
                "flagged_facts": ["forbidden facts that WERE mentioned"],
                "coverage": float (0.0-1.0),
                "notes": ["specific notes on accuracy"]
            }},
            "handling": {{
                "score": float (0-100),
                "resolution_signals": ["phrases indicating resolution steps"],
                "follow_up_signals": ["phrases indicating follow-up commitments"],
                "notes": ["specific notes on call handling"]
            }}
        }}
        
        Ensure the response is valid JSON.
        """

    async def _generate_with_openai(self, prompt: str) -> dict[str, Any]:
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert quality assurance analyst for call centers. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)

    async def _generate_with_gemini(self, prompt: str) -> dict[str, Any]:
        import asyncio
        response = await asyncio.to_thread(
            self.gemini_client.generate_content,
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)

    def _parse_result(self, result: dict[str, Any]) -> ScorecardResponse:
        empathy = EmpathyDetail(**result["empathy"])
        accuracy = AccuracyDetail(**result["accuracy"])
        handling = HandlingDetail(**result["handling"])

        return ScorecardResponse(
            overall_score=result["overall_score"],
            summary=result["summary"],
            highlights=result["highlights"],
            improvements=result["improvements"],
            empathy=empathy,
            accuracy=accuracy,
            handling=handling,
            generated_at=datetime.now(UTC)
        )
