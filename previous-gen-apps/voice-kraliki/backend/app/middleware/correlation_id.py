"""Correlation ID middleware for request tracing.

This middleware generates or extracts correlation IDs from incoming requests
and includes them in all logs and response headers for distributed tracing.
"""

import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.logging import clear_correlation_id, get_logger, set_correlation_id

logger = get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to handle correlation IDs for request tracing.

    This middleware:
    1. Extracts correlation ID from X-Correlation-ID header if present
    2. Generates new correlation ID if not present
    3. Sets correlation ID in request state and logging context
    4. Includes correlation ID in response headers
    """

    def __init__(
        self,
        app: ASGIApp,
        header_name: str = "X-Correlation-ID"
    ):
        """Initialize correlation ID middleware.

        Args:
            app: ASGI application
            header_name: Header name for correlation ID (default: X-Correlation-ID)
        """
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add correlation ID.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response: Response with correlation ID header
        """
        # Extract or generate correlation ID
        correlation_id = request.headers.get(self.header_name)

        if not correlation_id:
            # Generate new correlation ID
            correlation_id = str(uuid.uuid4())

        # Store in request state for access in route handlers
        request.state.correlation_id = correlation_id

        # Set in logging context for all logs in this request
        set_correlation_id(correlation_id)

        try:
            # Log request with correlation ID
            logger.info(
                "Request started",
                method=request.method,
                path=request.url.path,
                client_host=request.client.host if request.client else None,
                correlation_id=correlation_id
            )

            # Process request
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers[self.header_name] = correlation_id

            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                correlation_id=correlation_id
            )

            return response

        except Exception as exc:
            # Log exception with correlation ID
            logger.log_exception(
                "Request failed with exception",
                exc=exc,
                method=request.method,
                path=request.url.path,
                correlation_id=correlation_id
            )
            raise

        finally:
            # Clear correlation ID from context
            clear_correlation_id()


def get_correlation_id_from_request(request: Request) -> str:
    """Get correlation ID from request state.

    Args:
        request: FastAPI request object

    Returns:
        str: Correlation ID for this request
    """
    return getattr(request.state, "correlation_id", "unknown")
