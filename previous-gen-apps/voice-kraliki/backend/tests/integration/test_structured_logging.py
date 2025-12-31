#!/usr/bin/env python3
"""Test script to demonstrate structured logging output.

This script shows example log output in JSON format and validates
the structured logging system works correctly.
"""

import sys
import logging
from app.logging import (
    get_logger,
    LogContext,
    set_correlation_id,
    configure_root_logger
)


def main():
    """Run structured logging demonstration."""
    print("=" * 80)
    print("Structured Logging System Demonstration")
    print("=" * 80)
    print()

    # Configure root logger
    configure_root_logger(service_name="operator-demo", level=logging.INFO)

    # Get logger for this module
    logger = get_logger(__name__)

    print("1. Basic logging with contextual fields:")
    print("-" * 80)
    logger.info(
        "User logged in",
        user_id="user-123",
        username="john.doe",
        ip_address="192.168.1.100"
    )
    print()

    print("2. Logging with correlation ID:")
    print("-" * 80)
    set_correlation_id("abc-123-def-456")
    logger.info(
        "Processing API request",
        endpoint="/api/v1/orders",
        method="POST"
    )
    print()

    print("3. Using LogContext for related operations:")
    print("-" * 80)
    with LogContext(order_id="ord-789", customer_id="cust-456"):
        logger.info("Validating order")
        logger.info("Processing payment", amount=99.99, currency="USD")
        logger.info("Order completed successfully")
    print()

    print("4. Different log levels:")
    print("-" * 80)
    logger.debug("Debug message", detail="some debug info")
    logger.info("Info message", event="user_action")
    logger.warning("Warning message", threshold=95, limit=100)
    logger.error("Error message", error_type="ValidationError")
    print()

    print("5. Exception logging with stack trace:")
    print("-" * 80)
    try:
        result = 10 / 0
    except ZeroDivisionError as exc:
        logger.log_exception(
            "Division by zero error",
            exc=exc,
            operation="calculate_ratio",
            numerator=10,
            denominator=0
        )
    print()

    print("6. Telephony call simulation:")
    print("-" * 80)
    with LogContext(call_id="call-xyz", provider="twilio"):
        logger.info("Call initiated", direction="outbound", from_number="+1234567890")
        logger.info("Call answered", answer_time_ms=1234)
        logger.info("Call completed", duration_seconds=45, status="completed")
    print()

    print("7. WebSocket connection simulation:")
    print("-" * 80)
    set_correlation_id("ws-connection-123")
    with LogContext(session_id="session-abc", connection_type="websocket"):
        logger.info("WebSocket connection established", client_ip="192.168.1.100")
        logger.debug("Received audio frame", frame_size=1024, encoding="pcm")
        logger.info("WebSocket connection closed", reason="client_disconnect")
    print()

    print("=" * 80)
    print("Demonstration Complete")
    print("=" * 80)
    print()
    print("All logs above are in JSON format (one per line)")
    print("Each log includes:")
    print("  - timestamp (ISO 8601 UTC)")
    print("  - level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    print("  - service name")
    print("  - module and function name")
    print("  - correlation_id (when set)")
    print("  - all custom fields passed to the logger")
    print()
    print("These logs can be:")
    print("  - Parsed by log aggregation tools (ELK, Splunk, Datadog)")
    print("  - Searched and filtered by any field")
    print("  - Traced across services using correlation_id")
    print("  - Monitored with Prometheus metrics")
    print()


if __name__ == "__main__":
    main()
