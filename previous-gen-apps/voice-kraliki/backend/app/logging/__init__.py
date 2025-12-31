"""Structured logging system for Operator Demo 2026.

This package provides structured logging capabilities with JSON output,
correlation ID support, and Prometheus metrics integration.
"""

from app.logging.structured_logger import (
    LogContext,
    StructuredLogger,
    clear_correlation_id,
    configure_root_logger,
    get_correlation_id,
    get_logger,
    log_function_call,
    set_correlation_id,
)

__all__ = [
    "StructuredLogger",
    "LogContext",
    "get_logger",
    "configure_root_logger",
    "set_correlation_id",
    "get_correlation_id",
    "clear_correlation_id",
    "log_function_call",
]
