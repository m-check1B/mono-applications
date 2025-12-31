# Circuit Breaker Pattern Implementation

## Overview

The Circuit Breaker pattern prevents cascade failures in distributed systems by monitoring service health and automatically stopping requests to failing services. This implementation protects provider connections (Gemini, OpenAI, Deepgram) from cascade failures.

## Key Features

### State Machine
- **CLOSED**: Normal operation, all requests pass through
- **OPEN**: Failure threshold exceeded, requests fail immediately
- **HALF_OPEN**: Testing recovery, limited requests allowed

### Automatic Transitions
1. CLOSED → OPEN: After N consecutive failures
2. OPEN → HALF_OPEN: After timeout period
3. HALF_OPEN → CLOSED: After M consecutive successes
4. HALF_OPEN → OPEN: On any failure

### Monitoring & Metrics
- Prometheus metrics for state, calls, and transitions
- Comprehensive metrics tracking (success/failure/rejection rates)
- Real-time state visibility via health checks

### Thread Safety
- Async lock-based synchronization
- Safe for concurrent access across multiple sessions

## Usage

### Basic Usage

```python
from app.patterns.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

# Configure circuit breaker
config = CircuitBreakerConfig(
    name="gemini_provider",
    failure_threshold=5,
    timeout_seconds=60,
    success_threshold=2
)

breaker = CircuitBreaker(config, provider_id="gemini")

# Use as decorator
@breaker
async def call_gemini_api():
    return await gemini_client.generate()

# Or call directly
result = await breaker.call(call_gemini_api)
```

### Integration with Provider Orchestration

```python
from app.services.provider_orchestration import get_orchestrator

orchestrator = get_orchestrator()

# Call provider through circuit breaker
try:
    result = await orchestrator.call_provider_with_breaker(
        provider_id="gemini",
        func=gemini_api.generate,
        prompt="Hello"
    )
except CircuitBreakerOpenError as e:
    # Circuit is open, trigger failover
    logger.error(f"Circuit breaker open: {e}")
    await orchestrator.perform_failover(session_id)
```

### Health Checks

```python
# Get circuit breaker status for specific provider
status = orchestrator.get_circuit_breaker_status("gemini")
print(f"State: {status['state']}")
print(f"Success rate: {status['metrics']['success_rate']}%")

# Get all circuit breaker statuses
all_status = orchestrator.get_all_circuit_breaker_status()
for provider_id, status in all_status.items():
    print(f"{provider_id}: {status['state']}")
```

### Manual Control

```python
# Reset circuit breaker (administrative action)
await orchestrator.reset_circuit_breaker("gemini")

# Force open (maintenance mode)
await orchestrator.force_open_circuit_breaker("gemini")
```

## Configuration Parameters

### CircuitBreakerConfig

| Parameter | Default | Description |
|-----------|---------|-------------|
| `failure_threshold` | 5 | Consecutive failures before opening |
| `success_threshold` | 2 | Consecutive successes to close from HALF_OPEN |
| `timeout_seconds` | 60.0 | Time before transitioning OPEN → HALF_OPEN |
| `half_open_max_calls` | 3 | Max concurrent calls in HALF_OPEN state |
| `name` | "default" | Unique identifier for metrics |

### OrchestrationConfig

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_circuit_breaker` | True | Enable/disable circuit breaker |
| `circuit_breaker_failure_threshold` | 5 | Default failure threshold |
| `circuit_breaker_timeout_seconds` | 60.0 | Default timeout |
| `circuit_breaker_success_threshold` | 2 | Default success threshold |
| `circuit_breaker_half_open_max_calls` | 3 | Default max calls in HALF_OPEN |

## Prometheus Metrics

### Gauges
- `circuit_breaker_state{name, provider}`: Current state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)

### Counters
- `circuit_breaker_calls_total{name, provider, status}`: Total calls (attempted/success/failure/rejected)
- `circuit_breaker_state_transitions{name, provider, from_state, to_state}`: State changes

### Histograms
- `circuit_breaker_call_duration_seconds{name, provider, status}`: Call latency

## Architecture

### State Management

```
┌─────────────────────────────────────────────────┐
│                                                 │
│         Normal Operation (CLOSED)               │
│    All requests pass through normally           │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 │ failure_threshold reached
                 ▼
┌─────────────────────────────────────────────────┐
│                                                 │
│         Failure Mode (OPEN)                     │
│    All requests rejected immediately            │
│    Wait for timeout_seconds                     │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 │ timeout elapsed
                 ▼
┌─────────────────────────────────────────────────┐
│                                                 │
│         Testing Recovery (HALF_OPEN)            │
│    Limited requests allowed                     │
│    ┌──────────┬──────────┐                     │
│    │          │          │                      │
│    ▼          ▼          ▼                      │
│  Success  Success   Failure → OPEN              │
│    │          │                                  │
│    └──────────┴─→ success_threshold → CLOSED    │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Integration Points

1. **Provider Orchestration**: Filters out providers with OPEN circuits during selection
2. **Health Monitor**: Circuit breaker state contributes to provider health score
3. **Failover Service**: Circuit breaker triggers automatic failover
4. **Monitoring API**: Exposes circuit breaker status via HTTP endpoints

## Error Handling

### CircuitBreakerOpenError

Raised when attempting to call through an OPEN circuit:

```python
try:
    result = await breaker.call(provider_func)
except CircuitBreakerOpenError as e:
    # e.circuit_name: Name of the circuit breaker
    # e.retry_after: Seconds until circuit may close
    logger.error(f"Circuit {e.circuit_name} is open. Retry after {e.retry_after}s")
    # Implement fallback logic
```

## Best Practices

### 1. Configure Thresholds Appropriately
- Set `failure_threshold` based on expected error rates
- Use shorter timeouts for fast-recovering services
- Adjust `success_threshold` based on confidence needed

### 2. Monitor Circuit State
- Alert on state transitions to OPEN
- Track rejection rates in dashboards
- Monitor time spent in each state

### 3. Implement Fallbacks
- Always handle `CircuitBreakerOpenError`
- Have fallback providers ready
- Gracefully degrade service quality

### 4. Test Recovery
- Verify HALF_OPEN → CLOSED transitions work
- Test with realistic failure patterns
- Ensure manual reset works

### 5. Avoid Common Pitfalls
- Don't set thresholds too low (flapping)
- Don't set timeouts too short (no recovery time)
- Don't ignore circuit breaker state in load balancing

## Testing

Run the comprehensive test suite:

```bash
pytest backend/test_circuit_breaker.py -v
```

Tests cover:
- State transitions
- Failure/success thresholds
- Timeout behavior
- Metrics tracking
- Manual controls
- Edge cases

## Troubleshooting

### Circuit Breaker Keeps Opening

**Symptoms**: Circuit frequently transitions to OPEN
**Causes**:
- Provider is actually failing
- Failure threshold too low
- Network issues

**Solutions**:
- Check provider health and logs
- Increase failure threshold
- Investigate network connectivity

### Circuit Breaker Never Closes

**Symptoms**: Circuit stays OPEN indefinitely
**Causes**:
- Provider not recovering
- Success threshold too high
- Timeout too short

**Solutions**:
- Check provider status
- Manually reset after fixing provider
- Adjust configuration

### High Rejection Rate

**Symptoms**: Many calls rejected due to OPEN circuit
**Causes**:
- Legitimate failures triggering circuit
- No fallback mechanism
- Load imbalance

**Solutions**:
- Implement proper failover
- Add more healthy providers
- Rebalance load distribution

## References

- [Martin Fowler - Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Azure Architecture - Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
