"""Structured logging system with JSON output and correlation ID support.

This module provides a structured logging implementation that outputs JSON-formatted
logs with contextual information, correlation IDs for request tracing, and integration
with Prometheus metrics.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from functools import wraps
from typing import Any

from prometheus_client import Counter

# Context variable for correlation ID (thread-safe, async-safe)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)

# Context variable for additional fields
context_fields_var: ContextVar[dict[str, Any]] = ContextVar("context_fields", default={})


# Prometheus metrics for log events
log_events_total = Counter(
    "log_events_total",
    "Total log events by level",
    ["level", "service", "module"]
)

log_errors_total = Counter(
    "log_errors_total",
    "Total error and critical log events",
    ["service", "module", "error_type"]
)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Outputs logs as single-line JSON objects with all contextual information.
    """

    def __init__(self, service_name: str = "operator-demo"):
        """Initialize formatter with service name.

        Args:
            service_name: Name of the service for log identification
        """
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            str: JSON-formatted log entry
        """
        # Base log structure
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add correlation ID if present
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add context fields
        context_fields = context_fields_var.get()
        if context_fields:
            log_data.update(context_fields)

        # Add extra fields from log record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Handle exceptions
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stacktrace": self.formatException(record.exc_info),
            }

        # Add any additional attributes from the record
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "extra_fields"
            ]:
                # Skip private attributes and already included fields
                if not key.startswith("_"):
                    try:
                        # Only add JSON-serializable values
                        json.dumps(value)
                        log_data[key] = value
                    except (TypeError, ValueError):
                        log_data[key] = str(value)

        return json.dumps(log_data)


class StructuredLogger:
    """High-level structured logger with context management.

    Provides convenient methods for structured logging with automatic
    context propagation and Prometheus metrics integration.
    """

    def __init__(
        self,
        name: str,
        service_name: str = "operator-demo",
        level: int = logging.INFO
    ):
        """Initialize structured logger.

        Args:
            name: Logger name (typically module name)
            service_name: Service name for identification
            level: Minimum log level
        """
        self.service_name = service_name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Add JSON formatter to stdout
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter(service_name))
        self.logger.addHandler(handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def _log_with_metrics(
        self,
        level: int,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool | None = None
    ) -> None:
        """Internal method to log with metrics tracking.

        Args:
            level: Log level
            message: Log message
            extra: Additional fields
            exc_info: Include exception info
        """
        # Create log record with extra fields
        if extra:
            # Store extra fields in a way that StructuredFormatter can access
            record_extra = {"extra_fields": extra}
            self.logger.log(level, message, extra=record_extra, exc_info=exc_info)
        else:
            self.logger.log(level, message, exc_info=exc_info)

        # Track metrics
        level_name = logging.getLevelName(level)
        log_events_total.labels(
            level=level_name,
            service=self.service_name,
            module=self.logger.name
        ).inc()

        # Track errors separately
        if level >= logging.ERROR:
            error_type = extra.get("error_type", "unknown") if extra else "unknown"
            log_errors_total.labels(
                service=self.service_name,
                module=self.logger.name,
                error_type=error_type
            ).inc()

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message.

        Args:
            message: Log message
            **kwargs: Additional fields to include in log
        """
        self._log_with_metrics(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message.

        Args:
            message: Log message
            **kwargs: Additional fields to include in log
        """
        self._log_with_metrics(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message.

        Args:
            message: Log message
            **kwargs: Additional fields to include in log
        """
        self._log_with_metrics(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message.

        Args:
            message: Log message
            **kwargs: Additional fields to include in log
        """
        self._log_with_metrics(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message.

        Args:
            message: Log message
            **kwargs: Additional fields to include in log
        """
        self._log_with_metrics(logging.CRITICAL, message, kwargs)

    def log_exception(
        self,
        message: str,
        exc: Exception | None = None,
        **kwargs
    ) -> None:
        """Log an exception with full stack trace.

        Args:
            message: Log message
            exc: Exception to log (if None, uses sys.exc_info())
            **kwargs: Additional fields to include in log
        """
        if exc:
            kwargs["error_type"] = type(exc).__name__
            kwargs["error_message"] = str(exc)

        self._log_with_metrics(
            logging.ERROR,
            message,
            kwargs,
            exc_info=True if exc or sys.exc_info()[0] else None
        )


class LogContext:
    """Context manager for adding temporary fields to all logs.

    Example:
        with LogContext(user_id="123", request_id="abc"):
            logger.info("Processing request")  # Will include user_id and request_id
    """

    def __init__(self, **fields):
        """Initialize context with fields.

        Args:
            **fields: Key-value pairs to add to all logs within context
        """
        self.fields = fields
        self.token = None
        self.previous_context = None

    def __enter__(self):
        """Enter context and set fields."""
        self.previous_context = context_fields_var.get()
        # Merge with existing context
        new_context = {**self.previous_context, **self.fields}
        self.token = context_fields_var.set(new_context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore previous fields."""
        if self.token:
            context_fields_var.reset(self.token)
        return False


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context.

    Args:
        correlation_id: Correlation ID to set
    """
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> str | None:
    """Get current correlation ID.

    Returns:
        Optional[str]: Current correlation ID or None
    """
    return correlation_id_var.get()


def clear_correlation_id() -> None:
    """Clear correlation ID from current context."""
    correlation_id_var.set(None)


def log_function_call(logger: StructuredLogger):
    """Decorator to log function entry and exit.

    Args:
        logger: Logger instance to use

    Example:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(
                f"Entering {func.__name__}",
                function=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            try:
                result = func(*args, **kwargs)
                logger.debug(
                    f"Exiting {func.__name__}",
                    function=func.__name__
                )
                return result
            except Exception as exc:
                logger.log_exception(
                    f"Exception in {func.__name__}",
                    exc=exc,
                    function=func.__name__
                )
                raise
        return wrapper
    return decorator


def configure_root_logger(service_name: str = "operator-demo", level: int = logging.INFO):
    """Configure the root logger with structured formatting.

    This should be called once at application startup.

    Args:
        service_name: Service name for identification
        level: Minimum log level
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add structured formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter(service_name))
    root_logger.addHandler(handler)


def get_logger(name: str, service_name: str = "operator-demo") -> StructuredLogger:
    """Get or create a structured logger.

    Args:
        name: Logger name (typically __name__)
        service_name: Service name for identification

    Returns:
        StructuredLogger: Configured logger instance
    """
    return StructuredLogger(name, service_name)
