#!/usr/bin/env python3
"""Retry with exponential backoff for API failures.

From Cline research - graceful handling of rate limits and failures.

Usage:
    from control.retry import with_retry, RetryConfig

    @with_retry(max_attempts=3, base_delay=1.0)
    def call_api():
        return requests.get("https://api.example.com")

    # Or with custom config
    config = RetryConfig(
        max_attempts=5,
        base_delay=2.0,
        max_delay=60.0,
        exponential_base=2,
        retryable_exceptions=(ConnectionError, TimeoutError),
    )

    @with_retry(config=config)
    def call_flaky_api():
        ...
"""

import asyncio
import functools
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Callable, Tuple, Type, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    # Maximum number of attempts (including first try)
    max_attempts: int = 3

    # Base delay in seconds
    base_delay: float = 1.0

    # Maximum delay in seconds
    max_delay: float = 60.0

    # Exponential base (2 = double each time)
    exponential_base: float = 2.0

    # Add jitter to prevent thundering herd
    jitter: bool = True

    # Jitter range (0.0 to 1.0)
    jitter_range: float = 0.25

    # Exceptions that trigger retry
    retryable_exceptions: Tuple[Type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )

    # HTTP status codes that trigger retry (if checking response)
    retryable_status_codes: Tuple[int, ...] = (429, 500, 502, 503, 504)

    # Callback on retry (for logging/metrics)
    on_retry: Optional[Callable[[int, Exception, float], None]] = None


# Default config
DEFAULT_CONFIG = RetryConfig()


@dataclass
class RetryStats:
    """Statistics for retry operations."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_retries: int = 0
    total_delay_seconds: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[str] = None
    errors_by_type: dict = field(default_factory=dict)


# Global stats
_stats = RetryStats()


def get_retry_stats() -> dict:
    """Get current retry statistics."""
    return {
        "total_calls": _stats.total_calls,
        "successful_calls": _stats.successful_calls,
        "failed_calls": _stats.failed_calls,
        "total_retries": _stats.total_retries,
        "total_delay_seconds": round(_stats.total_delay_seconds, 2),
        "success_rate": round(_stats.successful_calls / max(_stats.total_calls, 1) * 100, 1),
        "last_error": _stats.last_error,
        "last_error_time": _stats.last_error_time,
        "errors_by_type": _stats.errors_by_type,
    }


def reset_retry_stats():
    """Reset retry statistics."""
    global _stats
    _stats = RetryStats()


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for a given attempt number.

    Uses exponential backoff with optional jitter.
    """
    # Exponential backoff: base_delay * (exponential_base ^ attempt)
    delay = config.base_delay * (config.exponential_base ** attempt)

    # Cap at max_delay
    delay = min(delay, config.max_delay)

    # Add jitter if enabled
    if config.jitter:
        jitter_amount = delay * config.jitter_range
        delay = delay + random.uniform(-jitter_amount, jitter_amount)

    return max(0, delay)


def with_retry(
    func: Callable = None,
    *,
    config: RetryConfig = None,
    max_attempts: int = None,
    base_delay: float = None,
    max_delay: float = None,
):
    """Decorator for retry with exponential backoff.

    Can be used with or without arguments:

        @with_retry
        def my_func():
            ...

        @with_retry(max_attempts=5)
        def my_func():
            ...

        @with_retry(config=RetryConfig(...))
        def my_func():
            ...
    """

    def decorator(fn):
        # Build config
        cfg = config or DEFAULT_CONFIG
        if max_attempts is not None:
            cfg = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay or cfg.base_delay,
                max_delay=max_delay or cfg.max_delay,
                exponential_base=cfg.exponential_base,
                jitter=cfg.jitter,
                retryable_exceptions=cfg.retryable_exceptions,
                retryable_status_codes=cfg.retryable_status_codes,
            )

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            global _stats
            _stats.total_calls += 1
            last_exception = None

            for attempt in range(cfg.max_attempts):
                try:
                    result = fn(*args, **kwargs)
                    _stats.successful_calls += 1
                    return result

                except cfg.retryable_exceptions as e:
                    last_exception = e
                    _stats.total_retries += 1

                    # Track error type
                    error_type = type(e).__name__
                    _stats.errors_by_type[error_type] = _stats.errors_by_type.get(error_type, 0) + 1

                    if attempt < cfg.max_attempts - 1:
                        delay = calculate_delay(attempt, cfg)
                        _stats.total_delay_seconds += delay

                        logger.warning(
                            f"Retry {attempt + 1}/{cfg.max_attempts} for {fn.__name__}: {e}. "
                            f"Waiting {delay:.2f}s"
                        )

                        if cfg.on_retry:
                            cfg.on_retry(attempt + 1, e, delay)

                        time.sleep(delay)
                    else:
                        _stats.failed_calls += 1
                        _stats.last_error = str(e)
                        _stats.last_error_time = datetime.now().isoformat()
                        raise

            # Should not reach here, but just in case
            _stats.failed_calls += 1
            raise last_exception

        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            global _stats
            _stats.total_calls += 1
            last_exception = None

            for attempt in range(cfg.max_attempts):
                try:
                    result = await fn(*args, **kwargs)
                    _stats.successful_calls += 1
                    return result

                except cfg.retryable_exceptions as e:
                    last_exception = e
                    _stats.total_retries += 1

                    error_type = type(e).__name__
                    _stats.errors_by_type[error_type] = _stats.errors_by_type.get(error_type, 0) + 1

                    if attempt < cfg.max_attempts - 1:
                        delay = calculate_delay(attempt, cfg)
                        _stats.total_delay_seconds += delay

                        logger.warning(
                            f"Retry {attempt + 1}/{cfg.max_attempts} for {fn.__name__}: {e}. "
                            f"Waiting {delay:.2f}s"
                        )

                        if cfg.on_retry:
                            cfg.on_retry(attempt + 1, e, delay)

                        await asyncio.sleep(delay)
                    else:
                        _stats.failed_calls += 1
                        _stats.last_error = str(e)
                        _stats.last_error_time = datetime.now().isoformat()
                        raise

            _stats.failed_calls += 1
            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper

    # Handle both @with_retry and @with_retry() syntax
    if func is not None:
        return decorator(func)
    return decorator


# Pre-configured retry decorators for common use cases
def retry_api(func):
    """Retry decorator for API calls (3 attempts, 1s base delay)."""
    return with_retry(
        func,
        config=RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=30.0,
            retryable_exceptions=(ConnectionError, TimeoutError, OSError),
        ),
    )


def retry_rate_limited(func):
    """Retry decorator for rate-limited APIs (5 attempts, 2s base delay)."""
    return with_retry(
        func,
        config=RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            max_delay=60.0,
            retryable_exceptions=(ConnectionError, TimeoutError, OSError),
        ),
    )


def retry_cli(func):
    """Retry decorator for CLI tool calls (3 attempts, 5s base delay)."""
    return with_retry(
        func,
        config=RetryConfig(
            max_attempts=3,
            base_delay=5.0,
            max_delay=120.0,
            retryable_exceptions=(OSError, subprocess.SubprocessError if 'subprocess' in dir() else OSError),
        ),
    )


if __name__ == "__main__":
    import json

    # Demo
    print("Retry with Exponential Backoff Demo")
    print("=" * 40)

    # Show delay progression
    print("\nDelay progression (base=1s, max=60s):")
    config = RetryConfig(base_delay=1.0, max_delay=60.0, jitter=False)
    for attempt in range(10):
        delay = calculate_delay(attempt, config)
        print(f"  Attempt {attempt}: {delay:.2f}s")

    # Test with a failing function
    print("\nTesting retry behavior:")

    call_count = 0

    @with_retry(max_attempts=3, base_delay=0.1)
    def flaky_function():
        global call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError(f"Simulated failure {call_count}")
        return "Success!"

    try:
        result = flaky_function()
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Failed: {e}")

    print(f"\n  Total calls: {call_count}")
    print(f"\nStats: {json.dumps(get_retry_stats(), indent=2)}")
