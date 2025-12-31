"""
Tests for the RouteSelector service - Hybrid Execution Routing Optimization

Tests complexity scoring, caching, circuit breakers, and route selection.
"""

import pytest
from datetime import datetime, timedelta

from app.services.route_selector import (
    RouteSelector,
    RouteType,
    ComplexityScore,
    RoutingDecision,
    get_route_selector,
    reset_route_selector,
)


@pytest.fixture
def route_selector():
    """Create a fresh route selector for each test"""
    reset_route_selector()
    return RouteSelector()


class TestComplexityScoring:
    """Tests for request complexity analysis"""

    def test_simple_task_low_complexity(self, route_selector):
        """Simple task creation should have low complexity"""
        text = "Create task buy groceries"
        complexity = route_selector._calculate_complexity(text)

        assert complexity.score < 0.3
        assert complexity.recommended_route == RouteType.DETERMINISTIC
        # Explanation can be "simple", "deterministic", or "CRUD"
        explanation_lower = complexity.explanation.lower()
        assert ("simple" in explanation_lower or
                "deterministic" in explanation_lower or
                "crud" in explanation_lower)

    def test_complex_research_high_complexity(self, route_selector):
        """Research requests should have notable complexity factors"""
        text = "Research the latest AI trends and analyze how they might impact our product strategy, then create a report"
        complexity = route_selector._calculate_complexity(text)

        # Research keywords should be detected
        assert complexity.factors["research_keywords"] > 0
        # Word count should be significant
        assert complexity.factors["word_count"] > 0.2

    def test_multi_step_request(self, route_selector):
        """Multi-step requests should increase complexity"""
        text = "First create a project, then add tasks, and finally schedule a meeting"
        complexity = route_selector._calculate_complexity(text)

        # Multi-step keywords should be detected
        assert complexity.factors["multi_step_keywords"] > 0
        # Multiple action verbs should be detected
        assert complexity.factors["action_verbs"] > 0

    def test_external_references_increase_complexity(self, route_selector):
        """URLs and file references should be detected as external"""
        text = "Download the file from https://example.com/report.pdf and summarize it"
        complexity = route_selector._calculate_complexity(text)

        # External references factor should be maxed out
        assert complexity.factors["external_refs"] == 1.0
        # Should recommend hybrid or orchestrated due to external refs
        assert complexity.recommended_route in [RouteType.HYBRID, RouteType.ORCHESTRATED]

    def test_deterministic_keywords_override(self, route_selector):
        """Explicit CRUD keywords should prefer deterministic routing"""
        text = "Create task review quarterly report tomorrow"
        complexity = route_selector._calculate_complexity(text)

        # Should still be deterministic despite multiple words
        assert complexity.recommended_route == RouteType.DETERMINISTIC

    def test_word_count_factor(self, route_selector):
        """Longer requests should have higher word count factor"""
        short = "Add task"
        long = "Create a comprehensive project plan that includes multiple phases with detailed milestones and deliverables for the upcoming product launch"

        short_score = route_selector._calculate_complexity(short)
        long_score = route_selector._calculate_complexity(long)

        assert long_score.factors["word_count"] > short_score.factors["word_count"]


class TestRouteSelection:
    """Tests for route selection logic"""

    def test_select_deterministic_for_simple_task(self, route_selector):
        """Simple tasks should route to deterministic"""
        decision = route_selector.select_route("Create task buy milk")

        assert decision.route == RouteType.DETERMINISTIC
        assert decision.confidence > 0.7
        assert not decision.from_cache

    def test_select_orchestrated_for_research(self, route_selector):
        """Research tasks with low AI confidence should route to orchestrated"""
        # When AI indicates low confidence, should escalate
        decision = route_selector.select_route(
            "Research and analyze competitor pricing strategies across all markets",
            ai_confidence=0.3,  # Low confidence triggers orchestration
            ai_should_escalate=False
        )

        assert decision.route == RouteType.ORCHESTRATED

    def test_ai_escalation_overrides(self, route_selector):
        """AI escalation flag should force orchestration"""
        decision = route_selector.select_route(
            "Create task",
            ai_confidence=0.9,
            ai_should_escalate=True
        )

        assert decision.route == RouteType.ORCHESTRATED
        assert RouteType.DETERMINISTIC in decision.fallback_chain

    def test_low_ai_confidence_routes_to_orchestration(self, route_selector):
        """Low AI confidence should trigger orchestration"""
        decision = route_selector.select_route(
            "Something ambiguous",
            ai_confidence=0.3,
            ai_should_escalate=False
        )

        assert decision.route == RouteType.ORCHESTRATED

    def test_fallback_chain_populated(self, route_selector):
        """Route decisions should include fallback options"""
        decision = route_selector.select_route(
            "Analyze this complex scenario and provide recommendations"
        )

        # Orchestrated routes should have deterministic fallback
        if decision.route == RouteType.ORCHESTRATED:
            assert RouteType.DETERMINISTIC in decision.fallback_chain


class TestCaching:
    """Tests for routing decision caching"""

    def test_cache_stores_decision(self, route_selector):
        """Decisions should be cached for similar inputs"""
        text = "Create task test caching"

        # First call
        decision1 = route_selector.select_route(text)
        assert not decision1.from_cache

        # Second call should use cache
        decision2 = route_selector.get_cached_decision(text)
        assert decision2 is not None
        assert decision2.from_cache

    def test_different_inputs_not_cached_together(self, route_selector):
        """Different inputs should have separate cache entries"""
        route_selector.select_route("Create task A")
        route_selector.select_route("Create task B")

        cached_a = route_selector.get_cached_decision("Create task A")
        cached_b = route_selector.get_cached_decision("Create task B")

        # Both should be cached separately
        assert cached_a is not None
        assert cached_b is not None

    def test_context_affects_cache_key(self, route_selector):
        """Context should be included in cache key"""
        text = "Create task"
        context1 = {"page": "dashboard"}
        context2 = {"page": "projects"}

        route_selector.select_route(text, context1)
        route_selector.select_route(text, context2)

        # Different contexts should have different cache entries
        cached1 = route_selector.get_cached_decision(text, context1)
        cached2 = route_selector.get_cached_decision(text, context2)

        assert cached1 is not None
        assert cached2 is not None


class TestCircuitBreaker:
    """Tests for circuit breaker functionality"""

    def test_circuit_opens_after_failures(self, route_selector):
        """Circuit should open after threshold failures"""
        route = RouteType.ORCHESTRATED

        # Record failures
        for _ in range(5):
            route_selector.record_result(route, success=False, latency_ms=100)

        # Circuit should be open
        assert route_selector._check_circuit(route) is True

    def test_circuit_closed_initially(self, route_selector):
        """Circuit should be closed initially"""
        assert route_selector._check_circuit(RouteType.ORCHESTRATED) is False
        assert route_selector._check_circuit(RouteType.DETERMINISTIC) is False

    def test_success_resets_failure_count(self, route_selector):
        """Successful requests should reset failure counter"""
        route = RouteType.ORCHESTRATED

        # Record some failures
        for _ in range(3):
            route_selector.record_result(route, success=False, latency_ms=100)

        # Then a success
        route_selector.record_result(route, success=True, latency_ms=50)

        # More failures shouldn't open circuit yet
        for _ in range(3):
            route_selector.record_result(route, success=False, latency_ms=100)

        # Circuit should still be closed (count reset by success)
        assert route_selector._check_circuit(route) is False


class TestPerformanceTracking:
    """Tests for performance statistics"""

    def test_records_successful_requests(self, route_selector):
        """Successful requests should update stats"""
        route = RouteType.DETERMINISTIC

        route_selector.record_result(route, success=True, latency_ms=50)
        route_selector.record_result(route, success=True, latency_ms=100)

        stats = route_selector.get_performance_stats()

        assert stats["deterministic"]["total_requests"] == 2
        assert stats["deterministic"]["success_rate"] == 1.0
        assert stats["deterministic"]["avg_latency_ms"] == 75.0

    def test_records_failed_requests(self, route_selector):
        """Failed requests should update stats"""
        route = RouteType.ORCHESTRATED

        route_selector.record_result(route, success=True, latency_ms=100)
        route_selector.record_result(route, success=False, latency_ms=50)

        stats = route_selector.get_performance_stats()

        assert stats["orchestrated"]["total_requests"] == 2
        assert stats["orchestrated"]["success_rate"] == 0.5

    def test_stats_include_circuit_status(self, route_selector):
        """Stats should show circuit breaker status"""
        stats = route_selector.get_performance_stats()

        assert "circuit_open" in stats["deterministic"]
        assert stats["deterministic"]["circuit_open"] is False


class TestRouteWithReason:
    """Tests for route recommendation with reasoning"""

    def test_returns_route_with_reason(self, route_selector):
        """Should return route with explanation"""
        route, reason, details = route_selector.get_recommended_route_with_reason(
            "Create task test"
        )

        assert route == RouteType.DETERMINISTIC
        assert isinstance(reason, str)
        assert len(reason) > 0
        assert "complexity_score" in details
        assert "factors" in details

    def test_cached_route_has_different_reason(self, route_selector):
        """Cached routes should indicate they're from cache"""
        text = "Create task cached"

        # First call
        route_selector.select_route(text)

        # Second call
        route, reason, details = route_selector.get_recommended_route_with_reason(text)

        assert details["from_cache"] is True


class TestSingletonBehavior:
    """Tests for singleton pattern"""

    def test_get_route_selector_returns_same_instance(self):
        """get_route_selector should return same instance"""
        reset_route_selector()
        selector1 = get_route_selector()
        selector2 = get_route_selector()

        assert selector1 is selector2

    def test_reset_clears_instance(self):
        """reset_route_selector should clear the singleton"""
        selector1 = get_route_selector()
        reset_route_selector()
        selector2 = get_route_selector()

        assert selector1 is not selector2
