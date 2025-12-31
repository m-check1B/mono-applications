"""WebSocket streaming module.

Handles real-time audio/text streaming via WebSocket connections.
"""

from app.streaming.websocket import create_websocket_handler

__all__ = ["create_websocket_handler"]
