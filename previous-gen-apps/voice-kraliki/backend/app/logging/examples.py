"""Examples demonstrating structured logging usage patterns.

This module provides examples of how to use the structured logging system
in various scenarios throughout the application.
"""

from app.logging import LogContext, get_logger, log_function_call

# ===== Basic Usage =====

logger = get_logger(__name__)

def basic_logging_example():
    """Example of basic logging with contextual fields."""
    # Simple log messages
    logger.info("User logged in")

    # Log with additional context
    logger.info(
        "User logged in",
        user_id="user-123",
        username="john.doe",
        ip_address="192.168.1.100"
    )

    # Log at different levels
    logger.debug("Debugging information", step=1, value="test")
    logger.warning("Rate limit approaching", current=95, limit=100)
    logger.error("Failed to process payment", error_type="PaymentError")
    logger.critical("Database connection lost", attempts=3)


# ===== Exception Logging =====

def exception_logging_example():
    """Example of logging exceptions with stack traces."""
    try:
        # Some operation that might fail
        result = 10 / 0
    except ZeroDivisionError as exc:
        # Log exception with full context
        logger.log_exception(
            "Division by zero error",
            exc=exc,
            operation="calculate_ratio",
            numerator=10,
            denominator=0
        )


# ===== Context Manager Usage =====

def context_manager_example():
    """Example of using LogContext to add fields to all logs."""
    # All logs within this context will include user_id and request_id
    with LogContext(user_id="user-456", request_id="req-abc"):
        logger.info("Processing user request")  # Includes user_id and request_id
        logger.info("Validating input")  # Also includes user_id and request_id

        # Nested contexts merge fields
        with LogContext(operation="update_profile"):
            logger.info("Updating user profile")  # Includes all three fields


# ===== Function Decorator Usage =====

@log_function_call(logger)
def decorated_function(user_id: str, action: str):
    """Example function with automatic entry/exit logging."""
    logger.info(
        "Performing action",
        user_id=user_id,
        action=action
    )
    return {"status": "success"}


# ===== Request Handler Example =====

async def handle_api_request_example():
    """Example of logging in an API request handler."""
    from fastapi import Request

    async def create_order(request: Request, order_data: dict):
        # Correlation ID is automatically available from middleware
        correlation_id = getattr(request.state, "correlation_id", None)

        logger.info(
            "Creating new order",
            order_id=order_data.get("id"),
            customer_id=order_data.get("customer_id"),
            items_count=len(order_data.get("items", []))
        )

        try:
            # Process order
            with LogContext(order_id=order_data["id"]):
                logger.debug("Validating order items")
                logger.debug("Checking inventory")
                logger.debug("Calculating total")

                logger.info(
                    "Order created successfully",
                    total=order_data.get("total")
                )

        except Exception as exc:
            logger.log_exception(
                "Failed to create order",
                exc=exc,
                order_data=order_data
            )
            raise


# ===== Telephony Call Example =====

def telephony_call_logging_example():
    """Example of logging telephony call events."""
    call_id = "call-789"
    provider = "twilio"

    with LogContext(call_id=call_id, provider=provider):
        logger.info(
            "Call initiated",
            direction="outbound",
            from_number="+1234567890",
            to_number="+0987654321"
        )

        logger.info("Call ringing")

        logger.info(
            "Call answered",
            answer_time_ms=1234
        )

        logger.info(
            "Call completed",
            duration_seconds=45,
            status="completed"
        )


# ===== WebSocket Connection Example =====

def websocket_logging_example():
    """Example of logging WebSocket events."""
    session_id = "session-xyz"

    with LogContext(session_id=session_id, connection_type="websocket"):
        logger.info(
            "WebSocket connection established",
            client_ip="192.168.1.100"
        )

        logger.debug(
            "Received audio frame",
            frame_size=1024,
            encoding="pcm"
        )

        logger.debug(
            "Sent text message",
            message_type="transcript",
            length=50
        )

        logger.info("WebSocket connection closed", reason="client_disconnect")


# ===== AI Provider Interaction Example =====

def ai_provider_logging_example():
    """Example of logging AI provider interactions."""
    provider = "openai"
    model = "gpt-4"

    with LogContext(provider=provider, model=model):
        logger.info(
            "Sending request to AI provider",
            prompt_tokens=150
        )

        try:
            # Simulate API call
            logger.debug("Waiting for AI response")

            logger.info(
                "Received AI response",
                response_tokens=250,
                latency_ms=1234,
                finish_reason="stop"
            )

        except Exception as exc:
            logger.log_exception(
                "AI provider request failed",
                exc=exc,
                error_type="APIError",
                retry_count=0
            )


# ===== Database Query Example =====

def database_query_logging_example():
    """Example of logging database operations."""
    with LogContext(component="database"):
        logger.debug(
            "Executing database query",
            operation="SELECT",
            table="users",
            filters={"status": "active"}
        )

        try:
            # Query execution
            logger.info(
                "Query completed",
                rows_returned=42,
                execution_time_ms=23
            )

        except Exception as exc:
            logger.log_exception(
                "Database query failed",
                exc=exc,
                operation="SELECT",
                table="users"
            )


# ===== Performance Monitoring Example =====

import time


def performance_monitoring_example():
    """Example of logging performance metrics."""
    operation_start = time.time()

    with LogContext(operation="process_batch"):
        logger.info("Starting batch processing", batch_size=100)

        for i in range(100):
            # Process items
            pass

        operation_duration = time.time() - operation_start

        logger.info(
            "Batch processing completed",
            items_processed=100,
            duration_seconds=operation_duration,
            items_per_second=100 / operation_duration
        )


# ===== Security Event Example =====

def security_logging_example():
    """Example of logging security-related events."""
    logger.warning(
        "Failed login attempt",
        username="admin",
        ip_address="192.168.1.100",
        attempt_count=3,
        security_event=True
    )

    logger.warning(
        "Rate limit exceeded",
        user_id="user-123",
        endpoint="/api/v1/login",
        limit=5,
        window="15min",
        security_event=True
    )

    logger.critical(
        "Potential security breach detected",
        event_type="unauthorized_access",
        resource="/admin/users",
        user_id="user-456",
        security_event=True,
        alert=True
    )
