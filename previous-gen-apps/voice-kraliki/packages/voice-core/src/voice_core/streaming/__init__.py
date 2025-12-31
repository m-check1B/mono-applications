"""Streaming utilities for voice-core.

Provides WebSocket handlers and audio streaming utilities.
"""

from voice_core.streaming.websocket import WebSocketBridge, create_websocket_bridge

__all__ = [
    "WebSocketBridge",
    "create_websocket_bridge",
]
