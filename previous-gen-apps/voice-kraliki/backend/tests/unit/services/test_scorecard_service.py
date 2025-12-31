import pytest

from app.models.scorecard import ScorecardRequest
from app.services.scorecard_service import ScorecardService


@pytest.mark.asyncio
async def test_scorecard_scores_when_signals_present() -> None:
    service = ScorecardService()
    request = ScorecardRequest(
        agent_transcript=(
            "I'm sorry to hear that. I understand the issue. "
            "I will open a ticket and follow up by email. "
            "We can also provide a refund if needed."
        ),
        customer_transcript="My order is broken. Can you help?",
        expected_facts=["ticket", "refund"],
    )

    result = await service.generate_scorecard(request)

    assert result.empathy.score >= 70
    assert result.accuracy.score == 100
    assert result.handling.score >= 70
    assert result.highlights


@pytest.mark.asyncio
async def test_scorecard_flags_missing_and_forbidden_facts() -> None:
    service = ScorecardService()
    request = ScorecardRequest(
        agent_transcript=(
            "We can refund the charge today. Please share your password to proceed."
        ),
        expected_facts=["refund", "ticket"],
        forbidden_facts=["password"],
    )

    result = await service.generate_scorecard(request)

    assert "ticket" in result.accuracy.missing_facts
    assert "password" in result.accuracy.flagged_facts
    assert result.accuracy.score < 100
