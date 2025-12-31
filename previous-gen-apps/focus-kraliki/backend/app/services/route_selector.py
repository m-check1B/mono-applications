"""
Intelligent Route Selector - Hybrid Execution Routing Optimization

This service optimizes the routing decision between:
- DETERMINISTIC: Fast local execution (tasks, projects, CRUD)
- ORCHESTRATED: Cloud AI execution (complex multi-step, research, automation)

Optimizations:
1. Request complexity scoring - Pre-filter before AI classification
2. Route decision caching - Similar inputs use cached decisions
3. Performance tracking - Track latency/success per route type
4. Smart fallback cascade - If orchestrated fails, fallback to deterministic
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RouteType(str, Enum):
    """Execution route types"""
    DETERMINISTIC = "deterministic"  # Fast, local
    ORCHESTRATED = "orchestrated"    # Cloud AI
    HYBRID = "hybrid"                # Start local, escalate if needed
    CACHED = "cached"                # Served from cache


@dataclass
class ComplexityScore:
    """Request complexity analysis result"""
    score: float  # 0.0 (simple) to 1.0 (complex)
    factors: Dict[str, float]  # Individual factor scores
    recommended_route: RouteType
    explanation: str


@dataclass
class RoutePerformance:
    """Performance metrics for a route type"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    last_failure: Optional[datetime] = None
    circuit_open: bool = False
    circuit_open_until: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    @property
    def avg_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests


@dataclass
class RoutingDecision:
    """Result of routing decision"""
    route: RouteType
    confidence: float
    from_cache: bool = False
    complexity_score: Optional[ComplexityScore] = None
    fallback_chain: List[RouteType] = field(default_factory=list)
    decision_time_ms: float = 0.0


class RouteSelector:
    """
    Intelligent route selector for hybrid execution.

    Uses complexity scoring, caching, and performance tracking
    to optimize routing decisions.
    """

    # Complexity scoring weights
    COMPLEXITY_FACTORS = {
        "word_count": 0.15,        # More words = more complex
        "question_marks": 0.10,    # Questions may need research
        "action_verbs": 0.20,      # Multiple actions = multi-step
        "external_refs": 0.25,     # URLs, files, APIs = orchestration
        "time_refs": 0.05,         # Scheduling complexity
        "multi_step_keywords": 0.15,  # "and then", "after that"
        "research_keywords": 0.10  # "find", "search", "analyze"
    }

    # Keywords that indicate orchestration is needed
    ORCHESTRATION_KEYWORDS = {
        "research", "analyze", "investigate", "find out", "look up",
        "automate", "integrate", "connect to", "api", "webhook",
        "browser", "website", "scrape", "download", "upload",
        "across", "multiple", "all my", "everything"
    }

    # Keywords that indicate deterministic is sufficient
    DETERMINISTIC_KEYWORDS = {
        "create task", "add task", "new task", "todo",
        "create project", "new project", "add project",
        "schedule", "reminder", "set time", "due date",
        "complete", "done", "finish", "mark as",
        "delete", "remove", "cancel", "update", "edit"
    }

    # Multi-step indicators
    MULTI_STEP_KEYWORDS = {
        "and then", "after that", "next", "finally",
        "first", "second", "third", "step 1", "step 2",
        "also", "additionally", "furthermore"
    }

    def __init__(self, cache_backend=None):
        """
        Initialize route selector.

        Args:
            cache_backend: Optional cache backend (Redis/memory).
                          If None, uses in-memory dict.
        """
        self._cache = cache_backend or {}
        self._performance: Dict[RouteType, RoutePerformance] = {
            RouteType.DETERMINISTIC: RoutePerformance(),
            RouteType.ORCHESTRATED: RoutePerformance(),
            RouteType.HYBRID: RoutePerformance(),
        }
        self._cache_ttl = timedelta(hours=1)
        self._circuit_timeout = timedelta(minutes=5)
        self._failure_threshold = 5  # Open circuit after 5 consecutive failures

    def _hash_input(self, text: str, context: Optional[Dict] = None) -> str:
        """Create cache key from input text and context"""
        normalized = text.lower().strip()
        # Include relevant context in hash
        ctx_str = str(sorted(context.items())) if context else ""
        content = f"{normalized}:{ctx_str}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _count_keywords(self, text: str, keywords: set) -> int:
        """Count how many keywords from set appear in text"""
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw in text_lower)

    def _calculate_complexity(self, text: str, context: Optional[Dict] = None) -> ComplexityScore:
        """
        Calculate request complexity score.

        Uses multiple factors to determine how complex a request is
        and whether it needs orchestration.
        """
        factors = {}
        text_lower = text.lower()
        words = text.split()

        # Factor 1: Word count (normalized to 0-1, caps at 50 words)
        word_count = len(words)
        factors["word_count"] = min(word_count / 50.0, 1.0)

        # Factor 2: Question marks
        question_count = text.count("?")
        factors["question_marks"] = min(question_count / 3.0, 1.0)

        # Factor 3: Action verbs (multiple actions = complex)
        action_verbs = {"create", "make", "add", "update", "delete", "find",
                        "search", "analyze", "send", "connect", "integrate"}
        action_count = sum(1 for w in words if w.lower() in action_verbs)
        factors["action_verbs"] = min(action_count / 4.0, 1.0)

        # Factor 4: External references (URLs, files, APIs)
        has_url = "http" in text_lower or "www." in text_lower
        has_file = any(ext in text_lower for ext in [".pdf", ".doc", ".xlsx", "file://"])
        has_api = "api" in text_lower or "webhook" in text_lower
        factors["external_refs"] = 1.0 if any([has_url, has_file, has_api]) else 0.0

        # Factor 5: Time references
        time_words = {"tomorrow", "today", "next week", "monday", "tuesday",
                      "wednesday", "thursday", "friday", "morning", "evening"}
        time_count = self._count_keywords(text, time_words)
        factors["time_refs"] = min(time_count / 2.0, 1.0)

        # Factor 6: Multi-step keywords
        multi_step_count = self._count_keywords(text, self.MULTI_STEP_KEYWORDS)
        factors["multi_step_keywords"] = min(multi_step_count / 2.0, 1.0)

        # Factor 7: Research keywords
        research_count = self._count_keywords(text, self.ORCHESTRATION_KEYWORDS)
        factors["research_keywords"] = min(research_count / 3.0, 1.0)

        # Calculate weighted score
        score = sum(
            factors[f] * self.COMPLEXITY_FACTORS[f]
            for f in self.COMPLEXITY_FACTORS
        )

        # Determine recommended route based on score
        if score < 0.3:
            recommended = RouteType.DETERMINISTIC
            explanation = "Simple request - deterministic execution"
        elif score < 0.6:
            recommended = RouteType.HYBRID
            explanation = "Moderate complexity - hybrid execution with escalation"
        else:
            recommended = RouteType.ORCHESTRATED
            explanation = "Complex request - full orchestration needed"

        # Override: Explicit deterministic keywords take precedence
        if self._count_keywords(text, self.DETERMINISTIC_KEYWORDS) > 0 and score < 0.5:
            recommended = RouteType.DETERMINISTIC
            explanation = "Explicit CRUD operation detected"

        return ComplexityScore(
            score=round(score, 3),
            factors={k: round(v, 3) for k, v in factors.items()},
            recommended_route=recommended,
            explanation=explanation
        )

    def _check_circuit(self, route: RouteType) -> bool:
        """Check if circuit breaker is open for a route"""
        perf = self._performance.get(route)
        if not perf:
            return False

        if perf.circuit_open:
            if perf.circuit_open_until and datetime.utcnow() < perf.circuit_open_until:
                return True  # Circuit still open
            else:
                # Circuit timeout expired, close it
                perf.circuit_open = False
                perf.circuit_open_until = None
                logger.info(f"Circuit breaker closed for {route.value}")

        return False

    def _open_circuit(self, route: RouteType):
        """Open circuit breaker for a route"""
        perf = self._performance.get(route)
        if perf:
            perf.circuit_open = True
            perf.circuit_open_until = datetime.utcnow() + self._circuit_timeout
            logger.warning(f"Circuit breaker opened for {route.value}")

    def get_cached_decision(self, text: str, context: Optional[Dict] = None) -> Optional[RoutingDecision]:
        """Check if we have a cached routing decision"""
        cache_key = self._hash_input(text, context)

        if isinstance(self._cache, dict):
            cached = self._cache.get(cache_key)
        else:
            # Redis-style cache
            cached = self._cache.get(cache_key)

        if cached:
            # Check if still valid
            if isinstance(cached, dict):
                cached_at = cached.get("cached_at")
                if cached_at:
                    age = datetime.utcnow() - datetime.fromisoformat(cached_at)
                    if age < self._cache_ttl:
                        return RoutingDecision(
                            route=RouteType(cached["route"]),
                            confidence=cached["confidence"],
                            from_cache=True,
                            decision_time_ms=0.1
                        )
        return None

    def cache_decision(self, text: str, decision: RoutingDecision, context: Optional[Dict] = None):
        """Cache a routing decision"""
        cache_key = self._hash_input(text, context)
        cached_data = {
            "route": decision.route.value,
            "confidence": decision.confidence,
            "cached_at": datetime.utcnow().isoformat()
        }

        if isinstance(self._cache, dict):
            self._cache[cache_key] = cached_data
        else:
            # Redis-style cache with TTL
            self._cache.set(cache_key, cached_data, ex=int(self._cache_ttl.total_seconds()))

    def select_route(
        self,
        text: str,
        context: Optional[Dict] = None,
        ai_confidence: Optional[float] = None,
        ai_should_escalate: Optional[bool] = None
    ) -> RoutingDecision:
        """
        Select the optimal execution route.

        Args:
            text: User input text
            context: Additional context (current page, user state, etc.)
            ai_confidence: Confidence from AI enhance-input (if available)
            ai_should_escalate: Escalation flag from AI (if available)

        Returns:
            RoutingDecision with selected route and metadata
        """
        start_time = time.time()

        # Check cache first
        cached = self.get_cached_decision(text, context)
        if cached:
            logger.debug(f"Using cached routing decision for input")
            return cached

        # Calculate complexity
        complexity = self._calculate_complexity(text, context)

        # Build fallback chain
        fallback_chain = []

        # Determine initial route
        if ai_should_escalate:
            # AI explicitly requested escalation
            route = RouteType.ORCHESTRATED
            confidence = ai_confidence or 0.9
            fallback_chain = [RouteType.HYBRID, RouteType.DETERMINISTIC]
        elif ai_confidence is not None and ai_confidence < 0.5:
            # Low confidence - use orchestration
            route = RouteType.ORCHESTRATED
            confidence = 1.0 - ai_confidence  # Invert for orchestration confidence
            fallback_chain = [RouteType.DETERMINISTIC]
        else:
            # Use complexity-based recommendation
            route = complexity.recommended_route
            confidence = 1.0 - complexity.score  # High complexity = lower deterministic confidence

            if route == RouteType.DETERMINISTIC:
                fallback_chain = []  # No fallback needed
            elif route == RouteType.HYBRID:
                fallback_chain = [RouteType.ORCHESTRATED, RouteType.DETERMINISTIC]
            else:
                fallback_chain = [RouteType.DETERMINISTIC]

        # Check circuit breakers
        if self._check_circuit(route):
            logger.warning(f"Circuit open for {route.value}, using fallback")
            if fallback_chain:
                route = fallback_chain[0]
                fallback_chain = fallback_chain[1:]
            else:
                route = RouteType.DETERMINISTIC

        decision_time = (time.time() - start_time) * 1000

        decision = RoutingDecision(
            route=route,
            confidence=round(confidence, 3),
            from_cache=False,
            complexity_score=complexity,
            fallback_chain=fallback_chain,
            decision_time_ms=round(decision_time, 2)
        )

        # Cache the decision
        self.cache_decision(text, decision, context)

        return decision

    def record_result(
        self,
        route: RouteType,
        success: bool,
        latency_ms: float
    ):
        """
        Record execution result for performance tracking.

        Args:
            route: Route that was used
            success: Whether execution succeeded
            latency_ms: Execution latency in milliseconds
        """
        perf = self._performance.get(route)
        if not perf:
            return

        perf.total_requests += 1

        if success:
            perf.successful_requests += 1
            perf.total_latency_ms += latency_ms
            # Reset failure counter on success
            perf.failed_requests = 0
        else:
            perf.failed_requests += 1
            perf.last_failure = datetime.utcnow()

            # Check if we should open circuit
            if perf.failed_requests >= self._failure_threshold:
                self._open_circuit(route)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all routes"""
        stats = {}
        for route, perf in self._performance.items():
            stats[route.value] = {
                "total_requests": perf.total_requests,
                "success_rate": round(perf.success_rate, 3),
                "avg_latency_ms": round(perf.avg_latency_ms, 2),
                "circuit_open": perf.circuit_open,
                "last_failure": perf.last_failure.isoformat() if perf.last_failure else None
            }
        return stats

    def get_recommended_route_with_reason(
        self,
        text: str,
        context: Optional[Dict] = None
    ) -> Tuple[RouteType, str, Dict[str, Any]]:
        """
        Get recommended route with detailed reasoning.

        Returns:
            Tuple of (route, reason_string, detailed_factors)
        """
        decision = self.select_route(text, context)

        if decision.from_cache:
            reason = "Cached decision from similar previous request"
            factors = {}
        else:
            complexity = decision.complexity_score
            reason = complexity.explanation if complexity else "Default routing"
            factors = complexity.factors if complexity else {}

        return decision.route, reason, {
            "complexity_score": decision.complexity_score.score if decision.complexity_score else 0,
            "factors": factors,
            "confidence": decision.confidence,
            "fallback_chain": [r.value for r in decision.fallback_chain],
            "from_cache": decision.from_cache,
            "decision_time_ms": decision.decision_time_ms
        }


# Singleton instance
_route_selector: Optional[RouteSelector] = None


def get_route_selector(cache_backend=None) -> RouteSelector:
    """Get or create the route selector singleton"""
    global _route_selector
    if _route_selector is None:
        _route_selector = RouteSelector(cache_backend)
    return _route_selector


def reset_route_selector():
    """Reset the route selector (for testing)"""
    global _route_selector
    _route_selector = None
