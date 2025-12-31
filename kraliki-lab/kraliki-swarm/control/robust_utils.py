#!/usr/bin/env python3
"""
Robust Utilities for Kraliki Automation
=======================================
Production-grade utilities for 24/7 autonomous operation.

Features:
- Retry with exponential backoff
- Circuit breaker pattern
- File locking for shared resources
- Centralized error tracking
- Health metrics
"""

import time
import json
import fcntl
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable, Any, Dict
from functools import wraps
from dataclasses import dataclass, asdict, field
from enum import Enum

GIN_DIR = Path(__file__).parent
ERRORS_FILE = GIN_DIR / "error-log.json"
HEALTH_FILE = GIN_DIR / "health-metrics.json"


# =============================================================================
# RETRY WITH EXPONENTIAL BACKOFF
# =============================================================================


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
):
    """
    Decorator for retry with exponential backoff.

    Usage:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def my_api_call():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        log_error(
                            source=func.__name__,
                            error_type="max_retries_exceeded",
                            message=str(e),
                            attempts=attempt + 1,
                        )
                        raise

                    delay = min(base_delay * (exponential_base**attempt), max_delay)
                    # Add jitter to prevent thundering herd
                    jitter = delay * 0.1 * (hash(str(time.time())) % 10) / 10
                    time.sleep(delay + jitter)

            raise last_exception

        return wrapper

    return decorator


# =============================================================================
# CIRCUIT BREAKER PATTERN
# =============================================================================


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreakerState:
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[str] = None
    last_success_time: Optional[str] = None
    open_events: list[str] = field(default_factory=list)
    success_times: list[str] = field(default_factory=list)
    failure_times: list[str] = field(default_factory=list)
    recovery_durations: list[float] = field(default_factory=list)
    last_open_time: Optional[str] = None
    adaptive_threshold: Optional[int] = None
    adaptive_recovery_timeout: Optional[int] = None
    last_tuned_at: Optional[str] = None


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.

    Usage:
        breaker = CircuitBreaker("linear_api", failure_threshold=5, recovery_timeout=60)

        if breaker.can_execute():
            try:
                result = api_call()
                breaker.record_success()
            except Exception as e:
                breaker.record_failure()
                raise
    """

    _instances: Dict[str, "CircuitBreaker"] = {}
    _state_file = GIN_DIR / "circuit-breakers.json"
    _self_healing_hook: Optional[Callable] = None  # Set later to avoid circular ref

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,  # seconds
        half_open_max_calls: int = 3,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.half_open_calls = 0
        self._tuning_open_window_hours = 6
        self._tuning_decay_window_hours = 24
        self._tuning_min_threshold = max(2, failure_threshold - 2)
        self._tuning_max_threshold = max(failure_threshold + 3, 8)
        self._tuning_min_recovery_timeout = max(30, recovery_timeout // 2)
        # Reduced max timeout from 900s to 300s (5 minutes max)
        self._tuning_max_recovery_timeout = max(recovery_timeout * 2, 300)
        self._tuning_calibration_window_minutes = 60
        self._tuning_min_samples = 6

        # Load state from disk
        self._load_state()
        self._normalize_tuning()

        # Register instance
        CircuitBreaker._instances[name] = self

    def _load_state(self):
        """Load circuit state from disk"""
        try:
            if self._state_file.exists():
                with open(self._state_file) as f:
                    all_states = json.load(f)
                    if self.name in all_states:
                        data = all_states[self.name]
                        self.state = CircuitBreakerState(
                            state=CircuitState(data.get("state", "closed")),
                            failure_count=data.get("failure_count", 0),
                            last_failure_time=data.get("last_failure_time"),
                            last_success_time=data.get("last_success_time"),
                            open_events=data.get("open_events", []),
                            success_times=data.get("success_times", []),
                            failure_times=data.get("failure_times", []),
                            recovery_durations=data.get("recovery_durations", []),
                            last_open_time=data.get("last_open_time"),
                            adaptive_threshold=data.get("adaptive_threshold"),
                            adaptive_recovery_timeout=data.get(
                                "adaptive_recovery_timeout"
                            ),
                            last_tuned_at=data.get("last_tuned_at"),
                        )
                        return
        except Exception:
            pass

        self.state = CircuitBreakerState()

    def _save_state(self):
        """Save circuit state to disk"""
        try:
            all_states = {}
            if self._state_file.exists():
                with open(self._state_file) as f:
                    all_states = json.load(f)

            all_states[self.name] = {
                "state": self.state.state.value,
                "failure_count": self.state.failure_count,
                "last_failure_time": self.state.last_failure_time,
                "last_success_time": self.state.last_success_time,
                "open_events": self.state.open_events,
                "success_times": self.state.success_times,
                "failure_times": self.state.failure_times,
                "recovery_durations": self.state.recovery_durations[-50:],
                "last_open_time": self.state.last_open_time,
                "adaptive_threshold": self.state.adaptive_threshold,
                "adaptive_recovery_timeout": self.state.adaptive_recovery_timeout,
                "last_tuned_at": self.state.last_tuned_at,
            }

            with open(self._state_file, "w") as f:
                json.dump(all_states, f, indent=2)
        except Exception:
            pass

    def _normalize_tuning(self):
        if self.state.adaptive_threshold is None:
            self.state.adaptive_threshold = self.failure_threshold
        if self.state.adaptive_recovery_timeout is None:
            self.state.adaptive_recovery_timeout = self.recovery_timeout

    def _prune_open_events(self, now: datetime) -> list[str]:
        cutoff = now - timedelta(hours=self._tuning_decay_window_hours)
        pruned = []
        for ts in self.state.open_events:
            try:
                parsed = datetime.fromisoformat(ts)
            except ValueError:
                continue
            if parsed >= cutoff:
                pruned.append(ts)
        return pruned

    def _prune_times(self, times: list[str], now: datetime) -> list[str]:
        cutoff = now - timedelta(hours=self._tuning_decay_window_hours)
        pruned = []
        for ts in times:
            try:
                parsed = datetime.fromisoformat(ts)
            except ValueError:
                continue
            if parsed >= cutoff:
                pruned.append(ts)
        return pruned

    def _recent_open_count(self, now: datetime) -> int:
        cutoff = now - timedelta(hours=self._tuning_open_window_hours)
        count = 0
        for ts in self.state.open_events:
            try:
                parsed = datetime.fromisoformat(ts)
            except ValueError:
                continue
            if parsed >= cutoff:
                count += 1
        return count

    def _calibrate_from_traffic(self, now: datetime):
        """Self-calibrate thresholds based on recent request volume and failure rate."""
        self.state.success_times = self._prune_times(self.state.success_times, now)
        self.state.failure_times = self._prune_times(self.state.failure_times, now)

        window_cutoff = now - timedelta(minutes=self._tuning_calibration_window_minutes)
        recent_success = [
            ts
            for ts in self.state.success_times
            if datetime.fromisoformat(ts) >= window_cutoff
        ]
        recent_fail = [
            ts
            for ts in self.state.failure_times
            if datetime.fromisoformat(ts) >= window_cutoff
        ]

        total = len(recent_success) + len(recent_fail)
        if total < self._tuning_min_samples:
            return

        failure_rate = len(recent_fail) / max(total, 1)
        calls_per_minute = total / max(self._tuning_calibration_window_minutes, 1)

        base_threshold = 2 + min(int(round(calls_per_minute)), 6)
        if failure_rate < 0.08:
            multiplier = 1.25
        elif failure_rate < 0.25:
            multiplier = 1.0
        else:
            multiplier = 0.7

        adaptive_threshold = int(round(base_threshold * multiplier))
        adaptive_threshold = max(
            self._tuning_min_threshold,
            min(self._tuning_max_threshold, adaptive_threshold),
        )

        if self.state.recovery_durations:
            sorted_durations = sorted(self.state.recovery_durations[-12:])
            median = sorted_durations[len(sorted_durations) // 2]
            adaptive_timeout = int(round(median * 1.5))
        else:
            adaptive_timeout = int(
                round(self.recovery_timeout * (1 + failure_rate * 3))
            )

        adaptive_timeout = max(
            self._tuning_min_recovery_timeout,
            min(self._tuning_max_recovery_timeout, adaptive_timeout),
        )

        self.state.adaptive_threshold = adaptive_threshold
        self.state.adaptive_recovery_timeout = adaptive_timeout
        self.state.last_tuned_at = now.isoformat()

    def _tune_on_open(self, now: datetime):
        """Increase thresholds/cooldowns when breaker opens frequently."""
        self.state.open_events = self._prune_open_events(now)
        self.state.open_events.append(now.isoformat())
        recent_opens = self._recent_open_count(now)

        adaptive_threshold = min(
            self._tuning_max_threshold, self.failure_threshold + recent_opens
        )
        adaptive_threshold = max(self._tuning_min_threshold, adaptive_threshold)

        # Reduced scaling from 120s per open to 30s per open
        # This prevents excessively long timeouts
        adaptive_timeout = min(
            self._tuning_max_recovery_timeout,
            self.recovery_timeout + (recent_opens * 30),
        )
        adaptive_timeout = max(self._tuning_min_recovery_timeout, adaptive_timeout)

        self.state.adaptive_threshold = adaptive_threshold
        self.state.adaptive_recovery_timeout = adaptive_timeout
        self.state.last_tuned_at = now.isoformat()
        self._calibrate_from_traffic(now)

    def _tune_on_close(self, now: datetime):
        """Drift back toward baseline when stable."""
        self.state.open_events = self._prune_open_events(now)
        adaptive_threshold = self.state.adaptive_threshold or self.failure_threshold
        adaptive_timeout = self.state.adaptive_recovery_timeout or self.recovery_timeout

        if not self.state.open_events:
            if adaptive_threshold > self.failure_threshold:
                adaptive_threshold -= 1
            elif adaptive_threshold < self.failure_threshold:
                adaptive_threshold += 1

            if adaptive_timeout > self.recovery_timeout:
                adaptive_timeout = max(self.recovery_timeout, adaptive_timeout - 60)
            elif adaptive_timeout < self.recovery_timeout:
                adaptive_timeout = min(self.recovery_timeout, adaptive_timeout + 60)

        self.state.adaptive_threshold = max(
            self._tuning_min_threshold, adaptive_threshold
        )
        self.state.adaptive_recovery_timeout = max(
            self._tuning_min_recovery_timeout, adaptive_timeout
        )
        self.state.last_tuned_at = now.isoformat()
        self._calibrate_from_traffic(now)

    def can_execute(self) -> bool:
        """Check if calls are allowed"""
        if self.state.state == CircuitState.CLOSED:
            return True

        if self.state.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.state.last_failure_time:
                last_failure = datetime.fromisoformat(self.state.last_failure_time)
                timeout = self.state.adaptive_recovery_timeout or self.recovery_timeout
                if datetime.now() - last_failure > timedelta(seconds=timeout):
                    self.state.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    self._save_state()
                    return True
            return False

        if self.state.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls

        return False

    def record_success(self):
        """Record a successful call"""
        now = datetime.now()
        self.state.last_success_time = now.isoformat()
        self.state.success_times.append(now.isoformat())
        if len(self.state.success_times) > 500:
            self.state.success_times = self.state.success_times[-500:]

        if self.state.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                # Recovered!
                self.state.state = CircuitState.CLOSED
                self.state.failure_count = 0
                if self.state.last_open_time:
                    try:
                        opened_at = datetime.fromisoformat(self.state.last_open_time)
                        duration = (now - opened_at).total_seconds()
                        self.state.recovery_durations.append(duration)
                    except ValueError:
                        pass
                self.state.last_open_time = None
                self._tune_on_close(now)
        elif self.state.state == CircuitState.CLOSED:
            last_tuned = self.state.last_tuned_at
            if last_tuned:
                try:
                    tuned_at = datetime.fromisoformat(last_tuned)
                    if now - tuned_at > timedelta(hours=1):
                        self._tune_on_close(now)
                except ValueError:
                    self._tune_on_close(now)

        self._save_state()

    def record_failure(self):
        """Record a failed call"""
        self.state.failure_count += 1
        now = datetime.now()
        self.state.last_failure_time = now.isoformat()
        self.state.failure_times.append(now.isoformat())
        if len(self.state.failure_times) > 500:
            self.state.failure_times = self.state.failure_times[-500:]
        state_changed = False

        if self.state.state == CircuitState.HALF_OPEN:
            # Failed during recovery test - back to open
            self.state.state = CircuitState.OPEN
            state_changed = True

        elif self.state.failure_count >= (
            self.state.adaptive_threshold or self.failure_threshold
        ):
            self.state.state = CircuitState.OPEN
            state_changed = True
            error_msg = f"Circuit opened after {self.state.failure_count} failures"
            log_error(
                source=f"circuit_breaker_{self.name}",
                error_type="circuit_open",
                message=error_msg,
            )
            # Trigger self-healing - create Linear ticket (deferred to avoid circular ref)
            if CircuitBreaker._self_healing_hook:
                CircuitBreaker._self_healing_hook(
                    self.name, self.state.failure_count, error_msg
                )

        if state_changed:
            self.state.last_open_time = now.isoformat()
            self._tune_on_open(now)
        else:
            self._calibrate_from_traffic(now)

        self._save_state()

    @classmethod
    def get_all_states(cls) -> Dict[str, Dict]:
        """Get state of all circuit breakers"""
        try:
            if cls._state_file.exists():
                with open(cls._state_file) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}


# =============================================================================
# FILE LOCKING FOR SHARED RESOURCES
# =============================================================================


class FileLock:
    """
    File-based locking for shared resources like features.json.

    Usage:
        with FileLock("/path/to/features.json"):
            # Safe to read/write
            data = json.load(f)
            data["key"] = "value"
            json.dump(data, f)
    """

    def __init__(self, file_path: str, timeout: float = 30.0):
        self.file_path = Path(file_path)
        self.lock_path = self.file_path.with_suffix(self.file_path.suffix + ".lock")
        self.timeout = timeout
        self._lock_file = None

    def __enter__(self):
        start = time.time()
        while True:
            try:
                # Use append mode to avoid truncating another process's lock
                # We don't unlink the lock file to avoid a race condition where
                # a new process opens a new inode while another holds the old one.
                self._lock_file = open(self.lock_path, "a")
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except (IOError, OSError):
                if time.time() - start > self.timeout:
                    raise TimeoutError(
                        f"Could not acquire lock on {self.file_path} within {self.timeout}s"
                    )
                time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._lock_file:
            try:
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
            finally:
                self._lock_file.close()
                self._lock_file = None


def atomic_json_update(file_path: str, update_func: Callable[[Dict], Dict]) -> Dict:
    """
    Atomically update a JSON file with locking.

    Usage:
        def add_feature(data):
            data["features"].append(new_feature)
            return data

        atomic_json_update("/path/to/features.json", add_feature)
    """
    path = Path(file_path)

    with FileLock(file_path):
        # Read
        if path.exists():
            with open(path) as f:
                data = json.load(f)
        else:
            data = {}

        # Update
        data = update_func(data)

        # Write atomically (to temp file, then rename)
        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        temp_path.rename(path)

        return data


# =============================================================================
# CENTRALIZED ERROR TRACKING
# =============================================================================


def log_error(source: str, error_type: str, message: str, **extra):
    """
    Log error to centralized error file for dashboard display.

    Usage:
        log_error(
            source="highway_coding",
            error_type="api_timeout",
            message="Linear API timeout after 30s",
            task_id="W4-015"
        )
    """
    error = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "type": error_type,
        "message": message,
        **extra,
    }

    try:
        errors = []
        if ERRORS_FILE.exists():
            with open(ERRORS_FILE) as f:
                errors = json.load(f)

        errors.append(error)

        # Keep last 100 errors
        errors = errors[-100:]

        with open(ERRORS_FILE, "w") as f:
            json.dump(errors, f, indent=2)
    except Exception:
        pass  # Don't fail if error logging fails


def get_recent_errors(limit: int = 20) -> list:
    """Get recent errors for dashboard"""
    try:
        if ERRORS_FILE.exists():
            with open(ERRORS_FILE) as f:
                errors = json.load(f)
                return errors[-limit:]
    except Exception:
        pass
    return []


# =============================================================================
# HEALTH METRICS
# =============================================================================


def update_health_metric(highway: str, metric: str, value: Any):
    """
    Update health metric for a highway.

    Usage:
        update_health_metric("coding", "cycles_completed", 150)
        update_health_metric("coding", "last_success", datetime.now().isoformat())
    """
    try:
        metrics = {}
        if HEALTH_FILE.exists():
            with open(HEALTH_FILE) as f:
                metrics = json.load(f)

        if highway not in metrics:
            metrics[highway] = {}

        metrics[highway][metric] = value
        metrics[highway]["updated_at"] = datetime.now().isoformat()

        with open(HEALTH_FILE, "w") as f:
            json.dump(metrics, f, indent=2)
    except Exception:
        pass


def get_all_health_metrics() -> Dict:
    """Get all health metrics for dashboard"""
    try:
        if HEALTH_FILE.exists():
            with open(HEALTH_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


# =============================================================================
# CONVENIENCE WRAPPERS
# =============================================================================


def robust_api_call(
    name: str,
    func: Callable,
    *args,
    max_retries: int = 3,
    circuit_failure_threshold: int = 5,
    **kwargs,
) -> Any:
    """
    Wrapper combining retry + circuit breaker for API calls.

    Usage:
        result = robust_api_call(
            "linear_create_issue",
            create_issue,
            title="Fix bug",
            description="..."
        )
    """
    breaker = CircuitBreaker(name, failure_threshold=circuit_failure_threshold)

    if not breaker.can_execute():
        raise RuntimeError(f"Circuit breaker open for {name}")

    @retry_with_backoff(max_retries=max_retries)
    def wrapped():
        return func(*args, **kwargs)

    try:
        result = wrapped()
        breaker.record_success()
        return result
    except Exception as e:
        breaker.record_failure()
        raise


# =============================================================================
# SELF-HEALING: AUTO-CREATE LINEAR TICKETS ON FAILURES
# =============================================================================

# Track recent auto-created tickets to avoid spam
_recent_healing_tickets: Dict[str, str] = {}  # hash -> timestamp
HEALING_COOLDOWN_HOURS = 4  # Don't create duplicate tickets within this window


def _ticket_hash(source: str, error_type: str) -> str:
    """Create hash for deduplication"""
    return hashlib.md5(f"{source}:{error_type}".encode()).hexdigest()[:12]


def _should_create_healing_ticket(source: str, error_type: str) -> bool:
    """Check if we should create a ticket (respects cooldown)"""
    ticket_hash = _ticket_hash(source, error_type)

    if ticket_hash in _recent_healing_tickets:
        last_created = datetime.fromisoformat(_recent_healing_tickets[ticket_hash])
        if datetime.now() - last_created < timedelta(hours=HEALING_COOLDOWN_HOURS):
            return False

    return True


def _record_healing_ticket(source: str, error_type: str):
    """Record that we created a ticket"""
    ticket_hash = _ticket_hash(source, error_type)
    _recent_healing_tickets[ticket_hash] = datetime.now().isoformat()

    # Persist to disk for cross-process dedup
    ticket_file = GIN_DIR / "healing-tickets.json"
    try:
        existing = {}
        if ticket_file.exists():
            with open(ticket_file) as f:
                existing = json.load(f)
        existing[ticket_hash] = datetime.now().isoformat()
        # Prune old entries
        cutoff = (
            datetime.now() - timedelta(hours=HEALING_COOLDOWN_HOURS * 2)
        ).isoformat()
        existing = {k: v for k, v in existing.items() if v > cutoff}
        with open(ticket_file, "w") as f:
            json.dump(existing, f)
    except Exception:
        pass


def _load_healing_tickets():
    """Load healing tickets from disk"""
    global _recent_healing_tickets
    ticket_file = GIN_DIR / "healing-tickets.json"
    try:
        if ticket_file.exists():
            with open(ticket_file) as f:
                _recent_healing_tickets = json.load(f)
    except Exception:
        pass


def trigger_self_healing(
    source: str, error_type: str, message: str, severity: str = "HIGH", **context
) -> bool:
    """
    Automatically create a Linear ticket when something breaks.

    Called by:
    - Circuit breakers when they open
    - Critical error handlers
    - Health check failures

    Returns:
        True if ticket created, False if skipped (cooldown/error)
    """
    _load_healing_tickets()

    if not _should_create_healing_ticket(source, error_type):
        return False  # Cooldown active

    try:
        # Import here to avoid circular imports
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent / "integrations"))
        from linear_client import create_issue, issue_exists

        title = f"[AUTO-FIX] {source}: {error_type}"

        # Check if similar issue already exists
        if issue_exists(title):
            _record_healing_ticket(
                source, error_type
            )  # Still record to avoid repeat checks
            return False

        description = f"""**Auto-generated by Kraliki Self-Healing**

## Error Details
- **Source:** {source}
- **Type:** {error_type}
- **Severity:** {severity}
- **Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Message
{message}

## Context
```json
{json.dumps(context, indent=2, default=str)}
```

## Action Required
Investigate and fix the root cause. This ticket was auto-created because:
- A circuit breaker tripped (sustained failures)
- A critical error occurred
- A health check failed

---
_Auto-generated by Kraliki Self-Healing System_
"""

        issue = create_issue(
            title=title,
            description=description,
            labels=[
                "stream:asset-engine",
                "type:bug",
                "phase:stability",
                "product:kraliki",
                f"source:{source}",
            ],
            priority=severity,
        )

        if issue:
            _record_healing_ticket(source, error_type)
            # Log success
            update_health_metric(
                "self_healing",
                "last_ticket_created",
                {
                    "timestamp": datetime.now().isoformat(),
                    "source": source,
                    "error_type": error_type,
                    "linear_id": issue.get("identifier"),
                },
            )
            return True

    except Exception as e:
        # Don't fail if self-healing fails - just log it
        log_error("self_healing", "ticket_creation_failed", str(e))

    return False


def self_healing_circuit_breaker_hook(
    breaker_name: str, failure_count: int, message: str
):
    """
    Hook called when circuit breaker opens.
    Creates Linear ticket for investigation.
    """
    trigger_self_healing(
        source=f"circuit_breaker_{breaker_name}",
        error_type="circuit_open",
        message=message,
        severity="HIGH",
        failure_count=failure_count,
        breaker_name=breaker_name,
    )


def self_healing_error_hook(source: str, error_type: str, message: str, **context):
    """
    Hook for critical errors that should trigger self-healing.
    """
    # Only trigger on specific severe error types
    critical_types = [
        "max_retries_exceeded",
        "circuit_open",
        "timeout",
        "api_error",
        "connection_error",
        "file_corruption",
    ]

    if error_type in critical_types:
        trigger_self_healing(
            source=source,
            error_type=error_type,
            message=message,
            severity="HIGH",
            **context,
        )


# Register the self-healing hook with CircuitBreaker
CircuitBreaker._self_healing_hook = self_healing_circuit_breaker_hook


# Quick test
if __name__ == "__main__":
    print("Testing robust utilities...")

    # Test retry
    @retry_with_backoff(max_retries=2, base_delay=0.1)
    def flaky_function():
        import random

        if random.random() < 0.7:
            raise ValueError("Random failure")
        return "success"

    try:
        result = flaky_function()
        print(f"Flaky function result: {result}")
    except ValueError as e:
        print(f"Flaky function failed: {e}")

    # Test circuit breaker
    breaker = CircuitBreaker("test", failure_threshold=2, recovery_timeout=5)
    print(f"Circuit state: {breaker.state.state.value}")

    # Test error logging
    log_error("test", "test_error", "This is a test error")
    print(f"Recent errors: {len(get_recent_errors())}")

    # Test health metrics
    update_health_metric("test", "test_metric", 42)
    print(f"Health metrics: {get_all_health_metrics()}")
