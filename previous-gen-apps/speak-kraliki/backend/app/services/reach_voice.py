"""
Speak by Kraliki - Reach Voice Client
Connects Speak (VoP) to Voice by Kraliki via Reach API.
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ReachVoiceError(RuntimeError):
    """Raised when Reach voice bootstrap fails."""


def _build_websocket_url(base_url: str, session_id: str) -> str:
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        raise ReachVoiceError("Reach voice API URL must include scheme and host")

    ws_scheme = "wss" if parsed.scheme == "https" else "ws"
    return f"{ws_scheme}://{parsed.netloc}/ws/sessions/{session_id}"


class ReachVoiceClient:
    """HTTP client for Voice by Kraliki session bootstrap."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def bootstrap_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = f"{self.base_url}/api/v1/sessions/bootstrap"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(endpoint, json=payload)

        if response.status_code >= 400:
            raise ReachVoiceError(
                f"Reach voice bootstrap failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        session_id = data.get("session_id")
        if not session_id:
            raise ReachVoiceError("Reach voice bootstrap missing session_id")

        data["websocket_url"] = _build_websocket_url(self.base_url, session_id)
        return data


def build_reach_client() -> ReachVoiceClient | None:
    if not settings.reach_voice_api_url:
        return None
    return ReachVoiceClient(settings.reach_voice_api_url)
