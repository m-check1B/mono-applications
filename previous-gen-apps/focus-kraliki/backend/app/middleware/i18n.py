"""
I18n Middleware - Automatically detect and set locale from requests
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.i18n import I18nHelper


class I18nMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically detect and set locale for each request.

    Adds 'locale' to request.state for use in route handlers.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and set locale.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response with locale set in request.state
        """
        # Detect locale from Accept-Language header or query param
        locale = I18nHelper.get_locale_from_request(request)

        # Store locale in request state for access in route handlers
        request.state.locale = locale

        # Add locale to response headers for client reference
        response = await call_next(request)
        response.headers["Content-Language"] = locale

        return response
