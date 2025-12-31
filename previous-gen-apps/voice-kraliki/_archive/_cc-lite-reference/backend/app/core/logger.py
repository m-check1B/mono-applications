"""
Structured logging configuration using structlog
Based on Stack 2026 standards
"""

import logging
import sys
from typing import Any
import structlog
from structlog.stdlib import LoggerFactory


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure structured logging with structlog

    Args:
        level: Logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR)
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if level <= logging.DEBUG else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )


def get_logger(name: str) -> Any:
    """
    Get a structured logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)
