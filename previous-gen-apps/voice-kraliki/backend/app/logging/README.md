# Structured Logging System

A comprehensive structured logging implementation for Operator Demo 2026 with JSON output, correlation ID support, and Prometheus metrics integration.

## Features

- **JSON Format**: All logs output as single-line JSON for easy parsing and aggregation
- **Correlation IDs**: Automatic request tracing across distributed systems
- **Context Management**: Add contextual fields that persist across multiple log statements
- **Prometheus Metrics**: Automatic tracking of log events and errors
- **Exception Handling**: Rich exception logging with stack traces
- **Performance**: Minimal overhead, async-safe, thread-safe
- **Easy Integration**: Simple API, works with existing Python logging

## Quick Start

### Basic Usage

```python
from app.logging import get_logger

logger = get_logger(__name__)

# Simple logging
logger.info("User logged in")

# Logging with context
logger.info(
    "Order created",
    order_id="ord-123",
    customer_id="cust-456",
    total=99.99
)
```

### Log Levels

```python
logger.debug("Debugging information", step=1)
logger.info("Informational message", event="user_login")
logger.warning("Warning message", threshold_exceeded=True)
logger.error("Error occurred", error_type="ValidationError")
logger.critical("Critical failure", service="database")
```

### Exception Logging

```python
try:
    result = process_payment(order)
except PaymentError as exc:
    logger.log_exception(
        "Payment processing failed",
        exc=exc,
        order_id=order.id,
        amount=order.total
    )
```

## Advanced Features

### Context Manager

Add fields to all logs within a context:

```python
from app.logging import LogContext

with LogContext(user_id="user-123", request_id="req-abc"):
    logger.info("Processing request")  # Includes user_id and request_id
    logger.info("Validating input")    # Also includes user_id and request_id

    # Nested contexts merge fields
    with LogContext(operation="update"):
        logger.info("Updating record")  # Includes all three fields
```

### Function Decorator

Automatically log function entry and exit:

```python
from app.logging import log_function_call

@log_function_call(logger)
def process_order(order_id: str):
    logger.info("Processing order", order_id=order_id)
    return {"status": "success"}
```

### Correlation IDs

Correlation IDs are automatically managed by the `CorrelationIdMiddleware`:

```python
from app.logging import get_correlation_id, set_correlation_id

# Get current correlation ID
correlation_id = get_correlation_id()

# Manually set correlation ID (usually not needed)
set_correlation_id("my-correlation-id")
```

In request handlers, correlation IDs are automatically available:

```python
from fastapi import Request

async def my_endpoint(request: Request):
    correlation_id = request.state.correlation_id
    logger.info("Processing request", correlation_id=correlation_id)
```

## Log Format

All logs are output as single-line JSON objects:

```json
{
  "timestamp": "2025-10-14T10:30:45.123456Z",
  "level": "INFO",
  "service": "operator-demo",
  "module": "telephony.routes",
  "function": "handle_call",
  "line": 42,
  "message": "Call initiated",
  "correlation_id": "abc-123-def-456",
  "call_id": "call-789",
  "provider": "twilio",
  "direction": "outbound"
}
```

### Standard Fields

Every log entry includes:

- `timestamp`: ISO 8601 timestamp in UTC
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `service`: Service name (operator-demo)
- `module`: Python module name
- `function`: Function name where log was created
- `line`: Line number
- `message`: Log message

### Optional Fields

- `correlation_id`: Request correlation ID (added by middleware)
- `exception`: Exception details (type, message, stacktrace)
- Any custom fields passed to the logger

## Configuration

### Application Startup

Configure structured logging in your application startup:

```python
from app.logging import configure_root_logger
import logging

# Configure at startup
configure_root_logger(
    service_name="operator-demo",
    level=logging.INFO  # or logging.DEBUG
)
```

This is already configured in `/backend/app/main.py` in the `lifespan` function.

### Middleware Setup

The correlation ID middleware is automatically added in `main.py`:

```python
from app.middleware.correlation_id import CorrelationIdMiddleware

app.add_middleware(CorrelationIdMiddleware)
```

## Prometheus Metrics

The logging system automatically tracks metrics:

### `log_events_total`

Counter of all log events by level, service, and module:

```
log_events_total{level="INFO", service="operator-demo", module="telephony.routes"} 42
log_events_total{level="ERROR", service="operator-demo", module="auth.routes"} 3
```

### `log_errors_total`

Counter of error and critical events by service, module, and error type:

```
log_errors_total{service="operator-demo", module="database", error_type="ConnectionError"} 5
log_errors_total{service="operator-demo", module="payments", error_type="PaymentError"} 2
```

## Best Practices

### 1. Use Contextual Fields

Instead of embedding data in messages, use structured fields:

```python
# Bad
logger.info(f"User {user_id} created order {order_id}")

# Good
logger.info("Order created", user_id=user_id, order_id=order_id)
```

### 2. Use Context Managers for Related Operations

```python
with LogContext(order_id=order.id):
    logger.info("Validating order")
    logger.info("Processing payment")
    logger.info("Sending confirmation")
```

### 3. Log Business Events, Not Implementation Details

```python
# Good - business event
logger.info("Payment processed", order_id=order.id, amount=order.total)

# Avoid - too low level
logger.debug("Calling stripe.charge.create()")
```

### 4. Include Error Types

```python
try:
    process_order(order)
except ValidationError as exc:
    logger.error("Order validation failed", error_type="ValidationError", order_id=order.id)
except PaymentError as exc:
    logger.error("Payment failed", error_type="PaymentError", order_id=order.id)
```

### 5. Use Appropriate Log Levels

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages about application flow
- `WARNING`: Something unexpected but handled (e.g., using defaults)
- `ERROR`: Error that prevented an operation but application continues
- `CRITICAL`: Severe error requiring immediate attention

## Integration Examples

### FastAPI Route Handler

```python
from app.logging import get_logger
from fastapi import Request

logger = get_logger(__name__)

@app.post("/api/orders")
async def create_order(request: Request, order_data: dict):
    # Correlation ID automatically available
    logger.info(
        "Creating order",
        customer_id=order_data["customer_id"],
        items_count=len(order_data["items"])
    )

    try:
        order = await order_service.create(order_data)
        logger.info("Order created successfully", order_id=order.id)
        return order
    except Exception as exc:
        logger.log_exception("Failed to create order", exc=exc)
        raise
```

### Background Task

```python
from app.logging import get_logger, LogContext

logger = get_logger(__name__)

async def process_batch_job(batch_id: str):
    with LogContext(batch_id=batch_id, job_type="batch_processing"):
        logger.info("Starting batch job")

        for item in items:
            with LogContext(item_id=item.id):
                logger.debug("Processing item")
                # ... process item

        logger.info("Batch job completed", items_processed=len(items))
```

### WebSocket Handler

```python
from app.logging import get_logger, set_correlation_id
import uuid

logger = get_logger(__name__)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Set correlation ID for websocket connection
    connection_id = str(uuid.uuid4())
    set_correlation_id(connection_id)

    logger.info("WebSocket connection established", connection_id=connection_id)

    try:
        while True:
            data = await websocket.receive_json()
            logger.debug("Received message", message_type=data.get("type"))
    except Exception as exc:
        logger.log_exception("WebSocket error", exc=exc)
```

## Testing

Example test for ensuring logging works correctly:

```python
import json
from app.logging import get_logger

def test_structured_logging(caplog):
    logger = get_logger("test")

    logger.info("Test message", user_id="123", action="test")

    # Parse JSON log output
    log_record = json.loads(caplog.records[0].message)

    assert log_record["level"] == "INFO"
    assert log_record["message"] == "Test message"
    assert log_record["user_id"] == "123"
    assert log_record["action"] == "test"
```

## Troubleshooting

### Logs Not Appearing

Ensure the log level is set correctly:

```python
configure_root_logger(service_name="operator-demo", level=logging.DEBUG)
```

### Duplicate Logs

Make sure you're not configuring the root logger multiple times. Configuration should happen once at startup.

### Correlation ID Not Present

Ensure `CorrelationIdMiddleware` is added to the FastAPI app before other middleware.

### Performance Issues

If logging is causing performance issues:
1. Use appropriate log levels (avoid DEBUG in production)
2. Don't log in tight loops
3. Consider async logging for high-throughput scenarios

## Migration from Print Statements

Replace existing print statements and unstructured logs:

```python
# Before
print(f"User {user_id} logged in")
logging.info(f"Processing order {order_id}")

# After
logger.info("User logged in", user_id=user_id)
logger.info("Processing order", order_id=order_id)
```

## See Also

- `examples.py` - Comprehensive usage examples
- `structured_logger.py` - Implementation details
- `/backend/app/middleware/correlation_id.py` - Correlation ID middleware
- Prometheus metrics documentation
