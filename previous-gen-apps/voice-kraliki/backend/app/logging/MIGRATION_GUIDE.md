# Migration Guide: Structured Logging

This guide helps you migrate existing code from unstructured logging (print statements, basic logging) to the new structured logging system.

## Quick Reference

### Before and After Examples

#### 1. Print Statements

```python
# Before
print(f"User {user_id} logged in from {ip_address}")
print("Processing order...")

# After
from app.logging import get_logger
logger = get_logger(__name__)

logger.info("User logged in", user_id=user_id, ip_address=ip_address)
logger.info("Processing order")
```

#### 2. Basic Logging

```python
# Before
import logging
logging.info(f"Call initiated: {call_id} to {phone_number}")
logging.error(f"Payment failed for order {order_id}: {error}")

# After
from app.logging import get_logger
logger = get_logger(__name__)

logger.info("Call initiated", call_id=call_id, phone_number=phone_number)
logger.error("Payment failed", order_id=order_id, error=str(error), error_type=type(error).__name__)
```

#### 3. Exception Logging

```python
# Before
import logging
try:
    process_payment()
except Exception as e:
    logging.error(f"Error processing payment: {e}")
    logging.exception("Payment processing failed")

# After
from app.logging import get_logger
logger = get_logger(__name__)

try:
    process_payment()
except Exception as exc:
    logger.log_exception("Payment processing failed", exc=exc, order_id=order_id)
```

#### 4. Request Handlers

```python
# Before
from fastapi import Request
import logging

@app.post("/api/orders")
async def create_order(request: Request, order: OrderCreate):
    logging.info(f"Creating order for customer {order.customer_id}")
    try:
        result = await order_service.create(order)
        logging.info(f"Order created: {result.id}")
        return result
    except Exception as e:
        logging.error(f"Failed to create order: {e}")
        raise

# After
from fastapi import Request
from app.logging import get_logger

logger = get_logger(__name__)

@app.post("/api/orders")
async def create_order(request: Request, order: OrderCreate):
    # correlation_id is automatically available from middleware
    logger.info("Creating order", customer_id=order.customer_id)
    try:
        result = await order_service.create(order)
        logger.info("Order created successfully", order_id=result.id)
        return result
    except Exception as exc:
        logger.log_exception("Failed to create order", exc=exc, customer_id=order.customer_id)
        raise
```

## Step-by-Step Migration

### Step 1: Import the Logger

At the top of your module, replace existing logging imports:

```python
# Remove
import logging
# Or
from logging import getLogger

# Add
from app.logging import get_logger

# At module level (after imports)
logger = get_logger(__name__)
```

### Step 2: Replace Print Statements

Find all print statements used for logging:

```bash
# Search for print statements
grep -n "print(" your_module.py
```

Replace each with appropriate log level:

```python
# Before
print("Starting process...")
print(f"Error: {error}")

# After
logger.info("Starting process")
logger.error("Process failed", error=str(error))
```

### Step 3: Convert String Interpolation to Structured Fields

Replace f-strings and format() with keyword arguments:

```python
# Before
logger.info(f"User {user_id} performed {action} on {resource}")

# After
logger.info("User performed action", user_id=user_id, action=action, resource=resource)
```

### Step 4: Add Context for Related Operations

Group related log statements with LogContext:

```python
# Before
logger.info(f"Processing order {order_id}")
logger.info(f"Validating order {order_id}")
logger.info(f"Order {order_id} completed")

# After
from app.logging import LogContext

with LogContext(order_id=order_id):
    logger.info("Processing order")
    logger.info("Validating order")
    logger.info("Order completed")
```

### Step 5: Update Exception Handling

Replace exception logging with log_exception:

```python
# Before
except Exception as e:
    logging.error(f"Failed: {e}")
    logging.exception("Stack trace:")

# After
except Exception as exc:
    logger.log_exception("Operation failed", exc=exc, additional_field="value")
```

## Migration Checklist

For each Python file in the backend:

- [ ] Import `get_logger` from `app.logging`
- [ ] Create module-level logger: `logger = get_logger(__name__)`
- [ ] Replace all `print()` statements with appropriate `logger.*()` calls
- [ ] Convert f-strings/format to structured fields (keyword arguments)
- [ ] Replace `logging.exception()` with `logger.log_exception()`
- [ ] Add `LogContext` for related operations
- [ ] Include relevant business fields (user_id, order_id, call_id, etc.)
- [ ] Add error_type for error logs
- [ ] Remove string concatenation from log messages

## Common Patterns

### Pattern 1: API Request Handler

```python
from app.logging import get_logger
from fastapi import Request

logger = get_logger(__name__)

@app.post("/api/resource")
async def create_resource(request: Request, data: ResourceCreate):
    logger.info(
        "Creating resource",
        resource_type=data.type,
        user_id=request.state.user_id if hasattr(request.state, 'user_id') else None
    )

    try:
        resource = await service.create(data)
        logger.info("Resource created successfully", resource_id=resource.id)
        return resource
    except ValidationError as exc:
        logger.error("Validation failed", error_type="ValidationError", details=str(exc))
        raise
    except Exception as exc:
        logger.log_exception("Failed to create resource", exc=exc)
        raise
```

### Pattern 2: Background Job

```python
from app.logging import get_logger, LogContext

logger = get_logger(__name__)

async def process_batch(batch_id: str, items: list):
    with LogContext(batch_id=batch_id, job_type="batch_processing"):
        logger.info("Starting batch job", items_count=len(items))

        for idx, item in enumerate(items):
            with LogContext(item_id=item.id, item_index=idx):
                try:
                    logger.debug("Processing item")
                    await process_item(item)
                    logger.debug("Item processed successfully")
                except Exception as exc:
                    logger.log_exception("Failed to process item", exc=exc)

        logger.info("Batch job completed")
```

### Pattern 3: External API Call

```python
from app.logging import get_logger
import time

logger = get_logger(__name__)

async def call_external_api(provider: str, endpoint: str):
    start_time = time.time()

    logger.info("Calling external API", provider=provider, endpoint=endpoint)

    try:
        response = await api_client.get(endpoint)
        latency = time.time() - start_time

        logger.info(
            "External API call successful",
            provider=provider,
            endpoint=endpoint,
            status_code=response.status_code,
            latency_ms=int(latency * 1000)
        )

        return response
    except Exception as exc:
        latency = time.time() - start_time
        logger.log_exception(
            "External API call failed",
            exc=exc,
            provider=provider,
            endpoint=endpoint,
            latency_ms=int(latency * 1000)
        )
        raise
```

### Pattern 4: Database Operations

```python
from app.logging import get_logger, LogContext
import time

logger = get_logger(__name__)

async def execute_query(query: str, params: dict):
    start_time = time.time()

    with LogContext(component="database", operation="query"):
        logger.debug("Executing query", query_type=query.split()[0])

        try:
            result = await db.execute(query, params)
            execution_time = time.time() - start_time

            logger.debug(
                "Query executed successfully",
                rows_affected=result.rowcount,
                execution_time_ms=int(execution_time * 1000)
            )

            return result
        except Exception as exc:
            logger.log_exception("Database query failed", exc=exc, query_type=query.split()[0])
            raise
```

## Testing Your Migration

### 1. Visual Inspection

Run your application and verify logs are in JSON format:

```bash
# Start the application
python -m uvicorn app.main:app

# Logs should look like:
# {"timestamp": "...", "level": "INFO", "message": "...", "user_id": "123", ...}
```

### 2. Check for Correlation IDs

Make an API request and verify correlation ID appears in logs:

```bash
curl -H "X-Correlation-ID: test-123" http://localhost:8000/health

# Check logs include: "correlation_id": "test-123"
```

### 3. Verify Exception Logging

Trigger an error and check the stack trace is included:

```python
# Logs should include:
# "exception": {
#   "type": "ValueError",
#   "message": "...",
#   "stacktrace": "..."
# }
```

### 4. Monitor Prometheus Metrics

Check that log metrics are being tracked:

```bash
curl http://localhost:8000/metrics | grep log_events_total
curl http://localhost:8000/metrics | grep log_errors_total
```

## Common Pitfalls

### 1. Don't Embed Data in Messages

```python
# Wrong
logger.info(f"User {user_id} created")

# Correct
logger.info("User created", user_id=user_id)
```

### 2. Don't Forget Error Types

```python
# Wrong
logger.error("Payment failed")

# Correct
logger.error("Payment failed", error_type="PaymentError")
```

### 3. Don't Use Generic Messages

```python
# Wrong
logger.info("Success")

# Correct
logger.info("Order created successfully", order_id=order_id)
```

### 4. Don't Over-Log

```python
# Wrong - too verbose
for item in items:
    logger.debug(f"Processing item {item.id}")

# Correct - log summary
logger.info("Processing batch", items_count=len(items))
```

## Rollout Strategy

### Phase 1: Critical Paths (Week 1)
- [ ] Authentication and authorization
- [ ] Payment processing
- [ ] Telephony call handling
- [ ] WebSocket connections

### Phase 2: API Endpoints (Week 2)
- [ ] User management endpoints
- [ ] Order management endpoints
- [ ] Campaign management endpoints
- [ ] Settings endpoints

### Phase 3: Background Jobs (Week 3)
- [ ] Scheduled tasks
- [ ] Batch processing
- [ ] Data synchronization
- [ ] Cleanup jobs

### Phase 4: Utilities (Week 4)
- [ ] Helper functions
- [ ] Middleware
- [ ] Database utilities
- [ ] External API clients

## Questions?

See the main README.md for usage examples or check examples.py for comprehensive patterns.
