"""Sentry error tracking configuration."""
import logging
import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """Initialize Sentry for error tracking and performance monitoring."""
    sentry_dsn = os.getenv("SENTRY_DSN")

    if not sentry_dsn:
        logger.warning("⚠️  SENTRY_DSN not configured - error tracking disabled")
        return

    environment = os.getenv("ENVIRONMENT", "production")
    release = os.getenv("RELEASE_VERSION", "unknown")

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=f"operator-demo@{release}",
        # Performance monitoring
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        # Profile performance
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        # Integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        # Error filtering
        before_send=before_send_filter,
        # Attach user context
        send_default_pii=False,  # Don't send PII by default
    )

    logger.info("✅ Sentry initialized for environment: %s", environment)


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry.
    Useful for ignoring known errors or adding custom logic.
    """
    # Ignore health check errors
    if event.get("request", {}).get("url", "").endswith("/health"):
        return None

    # Ignore rate limit errors (they're expected)
    if "rate_limit" in str(event.get("exception", {})).lower():
        return None

    return event


def capture_exception(error: Exception, context: dict = None) -> None:
    """
    Manually capture an exception with additional context.

    Args:
        error: The exception to capture
        context: Additional context (user, tags, extra data)
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            if "user" in context:
                scope.set_user(context["user"])
            if "tags" in context:
                for key, value in context["tags"].items():
                    scope.set_tag(key, value)
            if "extra" in context:
                for key, value in context["extra"].items():
                    scope.set_extra(key, value)

        sentry_sdk.capture_exception(error)
