# Structured Logging Quick Reference

## Setup (Once Per Module)

```python
from app.logging import get_logger

logger = get_logger(__name__)
```

## Basic Logging

```python
# Info
logger.info("User logged in", user_id="123")

# Debug
logger.debug("Processing step", step=1, detail="validation")

# Warning
logger.warning("Rate limit approaching", current=95, limit=100)

# Error
logger.error("Payment failed", error_type="PaymentError", order_id="456")

# Critical
logger.critical("Database connection lost", attempts=3)
```

## Exception Logging

```python
try:
    process_payment()
except Exception as exc:
    logger.log_exception(
        "Payment failed",
        exc=exc,
        order_id="123"
    )
```

## Context Manager

```python
from app.logging import LogContext

with LogContext(user_id="123", session_id="abc"):
    logger.info("Processing request")
    logger.info("Validation complete")
    # Both logs include user_id and session_id
```

## Correlation ID

```python
# In request handlers - automatic from middleware
correlation_id = request.state.correlation_id

# Manual set (WebSocket, background jobs)
from app.logging import set_correlation_id
set_correlation_id("my-unique-id")
```

## Common Patterns

### API Endpoint

```python
@app.post("/api/orders")
async def create_order(request: Request, order: OrderCreate):
    logger.info("Creating order", customer_id=order.customer_id)
    try:
        result = await service.create(order)
        logger.info("Order created", order_id=result.id)
        return result
    except Exception as exc:
        logger.log_exception("Order creation failed", exc=exc)
        raise
```

### Background Job

```python
async def process_batch(batch_id: str):
    with LogContext(batch_id=batch_id):
        logger.info("Starting batch", items_count=len(items))
        # Process items
        logger.info("Batch complete")
```

### External API Call

```python
logger.info("Calling external API", provider="twilio", endpoint="/calls")
try:
    response = await api.post("/calls")
    logger.info("API call success", status_code=response.status)
except Exception as exc:
    logger.log_exception("API call failed", exc=exc, provider="twilio")
```

## Best Practices

### ✅ DO

```python
logger.info("Order created", order_id="123", total=99.99)
logger.error("Payment failed", error_type="PaymentError", order_id="123")
```

### ❌ DON'T

```python
logger.info(f"Order {order_id} created with total {total}")  # Don't use f-strings
logger.error("Error occurred")  # Don't use generic messages
```

## Log Levels Guide

| Level | Use For | Example |
|-------|---------|---------|
| DEBUG | Diagnostic info | `logger.debug("SQL query", query=sql)` |
| INFO | Normal flow | `logger.info("User logged in", user_id="123")` |
| WARNING | Unexpected but handled | `logger.warning("Using default", key="timeout")` |
| ERROR | Operation failed | `logger.error("Payment failed", error_type="PaymentError")` |
| CRITICAL | Severe failure | `logger.critical("DB connection lost")` |

## Output Format

```json
{
  "timestamp": "2025-10-14T10:30:45.123Z",
  "level": "INFO",
  "service": "operator-demo",
  "module": "orders",
  "function": "create_order",
  "line": 42,
  "message": "Order created",
  "correlation_id": "abc-123",
  "order_id": "456",
  "customer_id": "789"
}
```

## Useful Fields

Always include these when relevant:

- `user_id` - User identifier
- `order_id` - Order identifier
- `call_id` - Call identifier
- `session_id` - Session identifier
- `provider` - External provider name
- `error_type` - Exception class name
- `operation` - Operation being performed
- `status` - Operation status

## See Also

- Full docs: `README.md`
- Examples: `examples.py`
- Migration: `MIGRATION_GUIDE.md`
