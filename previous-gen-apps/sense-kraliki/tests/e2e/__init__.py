"""E2E test module for Sense by Kraliki Bot."""

# Module availability checks
try:
    from app.bot import handlers
    from app.services import sensitivity, dreams, biorhythm, remedies, storage
    from app.data import astro

    _app_available = True
    _app_unavailable_reason = None
except ImportError as e:
    _app_available = False
    _app_unavailable_reason = f"App modules not available: {e}"

__all__ = ["_app_available", "_app_unavailable_reason"]
