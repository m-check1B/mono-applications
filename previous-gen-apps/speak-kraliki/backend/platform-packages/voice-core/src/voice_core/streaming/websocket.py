"""WebSocket bridge for connecting telephony to voice AI providers.

This module provides a bridge that connects telephony audio streams
to voice AI providers, handling format conversion and bidirectional streaming.
"""

import asyncio
import logging
from typing import Any, Callable, Awaitable

from voice_core.base import (
    AudioChunk,
    AudioFormat,
    ProviderEvent,
    RealtimeEndToEndProvider,
    SessionConfig,
    TelephonyAdapter,
)

logger = logging.getLogger(__name__)


class WebSocketBridge:
    """Bridge between telephony WebSocket and voice AI provider.

    Handles bidirectional audio streaming:
    - Telephony -> AI Provider (user speech)
    - AI Provider -> Telephony (AI response)
    """

    def __init__(
        self,
        provider: RealtimeEndToEndProvider,
        telephony: TelephonyAdapter,
        on_transcript: Callable[[str, str], Awaitable[None]] | None = None,
        on_function_call: Callable[[str, str, dict], Awaitable[dict]] | None = None,
    ):
        """Initialize WebSocket bridge.

        Args:
            provider: Voice AI provider (Gemini, OpenAI, etc.)
            telephony: Telephony adapter (Telnyx, Twilio)
            on_transcript: Callback for transcripts (role, text)
            on_function_call: Callback for function calls (call_id, name, args) -> result
        """
        self._provider = provider
        self._telephony = telephony
        self._on_transcript = on_transcript
        self._on_function_call = on_function_call
        self._running = False
        self._tasks: list[asyncio.Task] = []

    async def start(self, config: SessionConfig) -> None:
        """Start the bridge and connect to provider.

        Args:
            config: Session configuration for the voice provider
        """
        if self._running:
            raise RuntimeError("Bridge already running")

        self._running = True

        # Connect to voice provider
        await self._provider.connect(config)
        logger.info("WebSocket bridge started")

    async def stop(self) -> None:
        """Stop the bridge and disconnect."""
        self._running = False

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._tasks.clear()

        # Disconnect provider
        await self._provider.disconnect()
        logger.info("WebSocket bridge stopped")

    async def handle_telephony_audio(self, audio_data: bytes) -> None:
        """Handle incoming audio from telephony.

        Args:
            audio_data: Raw audio data from telephony
        """
        if not self._running:
            return

        try:
            # Convert telephony audio to unified format
            audio_chunk = await self._telephony.convert_audio_from_telephony(audio_data)

            # Send to voice provider
            await self._provider.send_audio(audio_chunk)

        except Exception as e:
            logger.error(f"Error handling telephony audio: {e}")

    async def process_provider_events(
        self,
        send_audio: Callable[[bytes], Awaitable[None]],
    ) -> None:
        """Process events from voice provider and send responses.

        Args:
            send_audio: Callback to send audio to telephony
        """
        try:
            async for event in self._provider.receive_events():
                if not self._running:
                    break

                await self._handle_provider_event(event, send_audio)

        except Exception as e:
            logger.error(f"Error processing provider events: {e}")

    async def _handle_provider_event(
        self,
        event: ProviderEvent,
        send_audio: Callable[[bytes], Awaitable[None]],
    ) -> None:
        """Handle a single provider event.

        Args:
            event: Provider event
            send_audio: Callback to send audio to telephony
        """
        if event.type == "audio.output":
            # Convert and send audio to telephony
            audio_chunk = AudioChunk(
                data=event.data["audio"],
                format=AudioFormat.PCM16,
                sample_rate=event.data.get("sample_rate", 24000),
            )
            telephony_audio = await self._telephony.convert_audio_to_telephony(audio_chunk)
            await send_audio(telephony_audio)

        elif event.type == "text.output":
            # Handle transcript
            if self._on_transcript:
                await self._on_transcript(
                    event.data.get("role", "assistant"),
                    event.data.get("text", ""),
                )

        elif event.type == "function_call":
            # Handle function call
            if self._on_function_call:
                call_id = event.data.get("call_id", "")
                name = event.data.get("name", "")
                arguments = event.data.get("arguments", {})

                try:
                    result = await self._on_function_call(call_id, name, arguments)
                    await self._provider.handle_function_result(call_id, result)
                except Exception as e:
                    logger.error(f"Function call {name} failed: {e}")
                    await self._provider.handle_function_result(
                        call_id, {"error": str(e)}
                    )

        elif event.type == "session.created":
            logger.info("Voice session created")

        elif event.type == "turn.started":
            logger.debug("AI turn started")

        elif event.type == "turn.completed":
            logger.debug("AI turn completed")

        elif event.type == "connection.reconnecting":
            logger.warning(
                f"Connection reconnecting (attempt {event.data.get('attempt')})"
            )

        elif event.type == "connection.reconnected":
            logger.info("Connection reconnected")

        elif event.type == "connection.failed":
            logger.error(f"Connection failed: {event.data.get('reason')}")


def create_websocket_bridge(
    provider: RealtimeEndToEndProvider,
    telephony: TelephonyAdapter,
    on_transcript: Callable[[str, str], Awaitable[None]] | None = None,
    on_function_call: Callable[[str, str, dict], Awaitable[dict]] | None = None,
) -> WebSocketBridge:
    """Factory function to create WebSocket bridge.

    Args:
        provider: Voice AI provider
        telephony: Telephony adapter
        on_transcript: Optional transcript callback
        on_function_call: Optional function call handler

    Returns:
        WebSocketBridge: Configured bridge instance
    """
    return WebSocketBridge(
        provider=provider,
        telephony=telephony,
        on_transcript=on_transcript,
        on_function_call=on_function_call,
    )
