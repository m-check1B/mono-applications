"""Design patterns for reliability and resilience.

This module contains implementations of common design patterns
for building reliable distributed systems.
"""

from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerState",
    "CircuitBreakerConfig",
]
