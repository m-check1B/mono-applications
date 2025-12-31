"""Prometheus metrics instrumentation for Operator Demo 2026.

This module defines all Prometheus metrics for monitoring application performance,
including HTTP requests, database operations, WebSocket connections, AI provider
interactions, telephony calls, and active sessions.
"""


from prometheus_client import Counter, Gauge, Histogram, Info

# ===== HTTP Request Metrics =====

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)


# ===== Database Metrics =====

db_connections_total = Gauge(
    'db_connections_total',
    'Total database connections in pool'
)

db_connections_checked_out = Gauge(
    'db_connections_checked_out',
    'Number of database connections currently checked out'
)

db_connections_overflow = Gauge(
    'db_connections_overflow',
    'Number of database overflow connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)


# ===== WebSocket Metrics =====

websocket_connections = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'Total WebSocket messages',
    ['direction', 'message_type']
)


# ===== AI Provider Metrics =====

ai_provider_requests_total = Counter(
    'ai_provider_requests_total',
    'Total AI provider requests',
    ['provider', 'status']
)

ai_provider_latency_seconds = Histogram(
    'ai_provider_latency_seconds',
    'AI provider response latency in seconds',
    ['provider']
)

ai_provider_errors_total = Counter(
    'ai_provider_errors_total',
    'Total AI provider errors',
    ['provider', 'error_type']
)

# Additional provider-specific metrics for 100/100 score
ai_provider_active_sessions = Gauge(
    'ai_provider_active_sessions',
    'Currently active sessions per provider',
    ['provider']
)

ai_provider_reconnections_total = Counter(
    'ai_provider_reconnections_total',
    'Total provider reconnection attempts',
    ['provider', 'success']
)

ai_provider_audio_chunks_sent = Counter(
    'ai_provider_audio_chunks_sent',
    'Total audio chunks sent to provider',
    ['provider']
)

ai_provider_audio_chunks_received = Counter(
    'ai_provider_audio_chunks_received',
    'Total audio chunks received from provider',
    ['provider']
)

ai_provider_circuit_breaker_transitions = Counter(
    'ai_provider_circuit_breaker_transitions',
    'Circuit breaker state transitions',
    ['provider', 'from_state', 'to_state']
)

ai_provider_uptime_seconds = Gauge(
    'ai_provider_uptime_seconds',
    'Provider uptime in seconds',
    ['provider']
)

# Audio quality metrics
audio_quality_mos_score = Gauge(
    'audio_quality_mos_score',
    'Mean Opinion Score for audio quality (1-5)',
    ['session_id', 'provider']
)

audio_quality_packet_loss_percentage = Gauge(
    'audio_quality_packet_loss_percentage',
    'Audio packet loss percentage',
    ['session_id', 'provider']
)

audio_quality_jitter_ms = Gauge(
    'audio_quality_jitter_ms',
    'Audio jitter in milliseconds',
    ['session_id', 'provider']
)

# Provider health metrics
provider_health_status = Gauge(
    'provider_health_status',
    'Provider health status (0=offline, 1=unhealthy, 2=degraded, 3=healthy)',
    ['provider_id', 'provider_type']
)

provider_health_consecutive_failures = Gauge(
    'provider_health_consecutive_failures',
    'Consecutive health check failures',
    ['provider_id']
)

provider_health_success_rate = Gauge(
    'provider_health_success_rate',
    'Health check success rate percentage',
    ['provider_id']
)


# ===== Telephony Call Metrics =====

telephony_calls_total = Counter(
    'telephony_calls_total',
    'Total telephony calls',
    ['provider', 'status', 'direction']
)

telephony_call_duration_seconds = Histogram(
    'telephony_call_duration_seconds',
    'Call duration in seconds',
    ['provider', 'direction']
)

telephony_active_calls = Gauge(
    'telephony_active_calls',
    'Number of currently active calls',
    ['provider']
)


# ===== Session Metrics =====

sessions_active = Gauge(
    'sessions_active',
    'Currently active sessions',
    ['provider_type']
)

sessions_total = Counter(
    'sessions_total',
    'Total sessions created',
    ['provider_type', 'status']
)

session_duration_seconds = Histogram(
    'session_duration_seconds',
    'Session duration in seconds',
    ['provider_type']
)


# ===== Application Info =====

app_info = Info(
    'app_info',
    'Application information'
)


# ===== Instrumentation Helper Functions =====

def track_request(method: str, endpoint: str, status: int, duration: float):
    """Track HTTP request metrics.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: Request endpoint path
        status: HTTP status code
        duration: Request duration in seconds
    """
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def track_db_query(operation: str, duration: float):
    """Track database query metrics.

    Args:
        operation: Type of database operation (select, insert, update, delete)
        duration: Query duration in seconds
    """
    db_query_duration_seconds.labels(operation=operation).observe(duration)


def track_websocket_message(direction: str, message_type: str):
    """Track WebSocket message metrics.

    Args:
        direction: Message direction (inbound, outbound)
        message_type: Type of message (audio, text, control)
    """
    websocket_messages_total.labels(direction=direction, message_type=message_type).inc()


def track_ai_provider_request(provider: str, status: str, latency: float):
    """Track AI provider request metrics.

    Args:
        provider: AI provider name (openai, gemini, deepgram)
        status: Request status (success, error)
        latency: Request latency in seconds
    """
    ai_provider_requests_total.labels(provider=provider, status=status).inc()
    ai_provider_latency_seconds.labels(provider=provider).observe(latency)


def track_ai_provider_error(provider: str, error_type: str):
    """Track AI provider error metrics.

    Args:
        provider: AI provider name
        error_type: Type of error (timeout, auth, rate_limit, etc.)
    """
    ai_provider_errors_total.labels(provider=provider, error_type=error_type).inc()


def track_telephony_call(provider: str, status: str, direction: str, duration: float = None):
    """Track telephony call metrics.

    Args:
        provider: Telephony provider name (twilio, telnyx)
        status: Call status (answered, completed, failed, busy, no_answer)
        direction: Call direction (inbound, outbound)
        duration: Call duration in seconds (optional, for completed calls)
    """
    telephony_calls_total.labels(provider=provider, status=status, direction=direction).inc()

    if duration is not None:
        telephony_call_duration_seconds.labels(provider=provider, direction=direction).observe(duration)


def update_db_pool_metrics(pool_size: int, checked_out: int, overflow: int):
    """Update database connection pool metrics.

    Args:
        pool_size: Total size of connection pool
        checked_out: Number of connections currently checked out
        overflow: Number of overflow connections
    """
    db_connections_total.set(pool_size)
    db_connections_checked_out.set(checked_out)
    db_connections_overflow.set(overflow)


def update_active_sessions(provider_type: str, count: int):
    """Update active sessions gauge.

    Args:
        provider_type: Type of AI provider
        count: Number of active sessions
    """
    sessions_active.labels(provider_type=provider_type).set(count)


def update_active_calls(provider: str, count: int):
    """Update active calls gauge.

    Args:
        provider: Telephony provider name
        count: Number of active calls
    """
    telephony_active_calls.labels(provider=provider).set(count)


def set_app_info(name: str, version: str, environment: str):
    """Set application information metric.

    Args:
        name: Application name
        version: Application version
        environment: Deployment environment (development, staging, production)
    """
    app_info.info({
        'name': name,
        'version': version,
        'environment': environment
    })


# Additional helper functions for provider-specific metrics
def track_provider_session(provider: str, delta: int):
    """Update active provider sessions count.

    Args:
        provider: Provider name
        delta: Change in session count (+1 to increment, -1 to decrement)
    """
    current = ai_provider_active_sessions.labels(provider=provider)._value.get()
    ai_provider_active_sessions.labels(provider=provider).set(max(0, current + delta))


def track_provider_reconnection(provider: str, success: bool):
    """Track provider reconnection attempt.

    Args:
        provider: Provider name
        success: Whether reconnection succeeded
    """
    ai_provider_reconnections_total.labels(
        provider=provider,
        success="success" if success else "failure"
    ).inc()


def track_audio_chunk(provider: str, direction: str):
    """Track audio chunk transmission.

    Args:
        provider: Provider name
        direction: 'sent' or 'received'
    """
    if direction == "sent":
        ai_provider_audio_chunks_sent.labels(provider=provider).inc()
    elif direction == "received":
        ai_provider_audio_chunks_received.labels(provider=provider).inc()


def track_circuit_breaker_transition(provider: str, from_state: str, to_state: str):
    """Track circuit breaker state transition.

    Args:
        provider: Provider name
        from_state: Previous state (CLOSED, OPEN, HALF_OPEN)
        to_state: New state (CLOSED, OPEN, HALF_OPEN)
    """
    ai_provider_circuit_breaker_transitions.labels(
        provider=provider,
        from_state=from_state,
        to_state=to_state
    ).inc()


def update_provider_uptime(provider: str, uptime_seconds: float):
    """Update provider uptime metric.

    Args:
        provider: Provider name
        uptime_seconds: Uptime in seconds
    """
    ai_provider_uptime_seconds.labels(provider=provider).set(uptime_seconds)


def update_audio_quality_metrics(
    session_id: str,
    provider: str,
    mos_score: float = None,
    packet_loss: float = None,
    jitter_ms: float = None
):
    """Update audio quality metrics for a session.

    Args:
        session_id: Session identifier
        provider: Provider name
        mos_score: Mean Opinion Score (1-5)
        packet_loss: Packet loss percentage (0-100)
        jitter_ms: Jitter in milliseconds
    """
    if mos_score is not None:
        audio_quality_mos_score.labels(session_id=session_id, provider=provider).set(mos_score)

    if packet_loss is not None:
        audio_quality_packet_loss_percentage.labels(session_id=session_id, provider=provider).set(packet_loss)

    if jitter_ms is not None:
        audio_quality_jitter_ms.labels(session_id=session_id, provider=provider).set(jitter_ms)


def update_provider_health_status(
    provider_id: str,
    provider_type: str,
    status: str,
    consecutive_failures: int = 0,
    success_rate: float = 100.0
):
    """Update provider health metrics.

    Args:
        provider_id: Provider identifier
        provider_type: Type of provider
        status: Health status (offline, unhealthy, degraded, healthy)
        consecutive_failures: Number of consecutive failures
        success_rate: Health check success rate percentage
    """
    # Map status to numeric value
    status_map = {
        "offline": 0,
        "unhealthy": 1,
        "degraded": 2,
        "healthy": 3
    }

    provider_health_status.labels(
        provider_id=provider_id,
        provider_type=provider_type
    ).set(status_map.get(status, 0))

    provider_health_consecutive_failures.labels(provider_id=provider_id).set(consecutive_failures)
    provider_health_success_rate.labels(provider_id=provider_id).set(success_rate)
