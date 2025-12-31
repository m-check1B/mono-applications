"""WebSocket handler for real-time audio/text streaming.

Manages bidirectional communication between clients and AI providers.
"""

import asyncio
import base64
import json
import logging
from typing import Any
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect

from app.providers.base import AudioChunk, AudioFormat, ProviderEvent, TextMessage
from app.services.ai_insights import ai_insights_service
from app.services.context_sharing import (
    ChannelType,
    ContextEvent,
    ContextEventType,
    context_sharing_service,
)
from app.sessions.manager import get_session_manager

logger = logging.getLogger(__name__)


class WebSocketStreamHandler:
    """Handles WebSocket streaming for a session.

    Coordinates between client WebSocket and AI provider.
    """

    def __init__(self, websocket: WebSocket, session_id: UUID):
        """Initialize WebSocket handler.

        Args:
            websocket: FastAPI WebSocket connection
            session_id: Associated session ID
        """
        self.websocket = websocket
        self.session_id = session_id
        self.session_manager = get_session_manager()
        self._running = False
        self.conversation_history = []

    async def handle(self) -> None:
        """Main handler loop for WebSocket connection.

        Manages bidirectional streaming between client and provider.
        """
        try:
            # Accept WebSocket connection
            await self.websocket.accept()
            logger.info(f"WebSocket connected for session {self.session_id}")

            # Get session and provider
            session = self.session_manager.get_session(self.session_id)
            if not session:
                await self._send_error("Session not found")
                return

            provider = self.session_manager.get_provider(self.session_id)
            if not provider:
                await self._send_error("Provider not initialized")
                return

            self._running = True

            # Start two concurrent tasks:
            # 1. Receive from client and forward to provider
            # 2. Receive from provider and forward to client
            await asyncio.gather(
                self._client_to_provider_loop(provider),
                self._provider_to_client_loop(provider),
                return_exceptions=True,
            )

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {self.session_id}")
        except Exception as e:
            logger.error(f"WebSocket error for session {self.session_id}: {e}")
            await self._send_error(str(e))
        finally:
            self._running = False
            await self.session_manager.end_session(self.session_id)
            await self.websocket.close()

    async def _client_to_provider_loop(self, provider: Any) -> None:
        """Receive messages from client and forward to provider.

        Args:
            provider: AI provider instance
        """
        try:
            while self._running:
                # Receive message from client
                message = await self.websocket.receive()

                # Handle different message types
                if "text" in message:
                    raw_text = message["text"]
                    if await self._handle_twilio_payload(provider, raw_text):
                        continue
                    await self._handle_text_message(provider, raw_text)
                elif "bytes" in message:
                    await self._handle_audio_message(provider, message["bytes"])

        except WebSocketDisconnect:
            logger.info("Client disconnected")
            self._running = False
        except Exception as e:
            logger.error(f"Error in client->provider loop: {e}")
            self._running = False

    async def _provider_to_client_loop(self, provider: Any) -> None:
        """Receive events from provider and forward to client.

        Args:
            provider: AI provider instance
        """
        try:
            async for event in provider.receive_events():
                await self._forward_provider_event(event)

        except Exception as e:
            logger.error(f"Error in provider->client loop: {e}")
            self._running = False

    async def _handle_text_message(self, provider: Any, text: str) -> None:
        """Handle text message from client.

        Args:
            provider: AI provider instance
            text: JSON text message
        """
        try:
            data = json.loads(text)
            message_type = data.get("type")

            if message_type == "ping":
                # Handle heartbeat ping
                await self._handle_ping_message(data)

            elif message_type == "text":
                # Forward text to provider
                content = data.get("content", "")
                text_msg = TextMessage(
                    role="user",
                    content=content,
                )
                await provider.send_text(text_msg)

                # Generate AI insights for user messages
                await self._generate_ai_insights(content, "user")

            elif message_type == "function_result":
                # Handle function result
                call_id = data.get("call_id")
                result = data.get("result", {})
                await provider.handle_function_result(call_id, result)

            elif message_type == "suggestion-action":
                # Handle suggestion action
                await self._handle_suggestion_action(data)

            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from client: {e}")
        except Exception as e:
            logger.error(f"Error handling text message: {e}")

    async def _handle_ping_message(self, ping_data: dict[str, Any]) -> None:
        """Handle heartbeat ping from client.
        
        Args:
            ping_data: Ping message data
        """
        try:
            # Send pong response
            pong_response = {
                "type": "pong",
                "timestamp": ping_data.get("timestamp"),
                "server_timestamp": int(asyncio.get_event_loop().time() * 1000),
                "session_id": str(self.session_id)
            }
            await self.websocket.send_json(pong_response)
            logger.debug(f"Sent pong response for session {self.session_id}")

        except Exception as e:
            logger.error(f"Failed to send pong response: {e}")

    async def _handle_twilio_payload(self, provider: Any, raw_text: str) -> bool:
        """Handle Twilio MediaStream JSON payloads if present.

        Args:
            provider: Current AI provider
            raw_text: Raw JSON text from websocket

        Returns:
            bool: True if the payload was handled as Twilio media event.
        """

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            return False

        event = data.get("event")
        if not event:
            return False

        if event == "media":
            media = data.get("media", {})
            chunk = self._twilio_media_to_chunk(media)
            if chunk:
                try:
                    await provider.send_audio(chunk)
                except Exception as exc:  # pragma: no cover - provider errors logged elsewhere
                    logger.error("Failed to send Twilio media chunk: %s", exc)
            return True

        if event in {"start", "connected", "stop", "mark", "close"}:
            logger.debug("Twilio event %s for session %s", event, self.session_id)
            return True

        return False

    async def _handle_audio_message(self, provider: Any, audio_data: bytes) -> None:
        """Handle audio message from client.

        Args:
            provider: AI provider instance
            audio_data: Raw audio bytes (PCM16)
        """
        try:
            # Create audio chunk
            audio_chunk = AudioChunk(
                data=audio_data,
                format=AudioFormat.PCM16,
                sample_rate=16000,  # Default sample rate
            )

            # Forward to provider
            await provider.send_audio(audio_chunk)

        except Exception as e:
            logger.error(f"Error handling audio message: {e}")

    async def _forward_provider_event(self, event: ProviderEvent) -> None:
        """Forward provider event to client via WebSocket.

        Args:
            event: Event from provider
        """
        try:
            # Capture event for context sharing
            await self._capture_event_for_sharing(event)

            if event.type == "audio.output":
                # Send audio as binary
                audio_data = event.data.get("audio", b"")
                await self.websocket.send_bytes(audio_data)

            else:
                # Send other events as JSON
                await self.websocket.send_json({
                    "type": event.type,
                    "data": event.data,
                })

        except Exception as e:
            logger.error(f"Error forwarding provider event: {e}")

    async def _capture_event_for_sharing(self, event: ProviderEvent) -> None:
        """Capture relevant provider events for context sharing service.
        
        Args:
            event: Provider event to capture
        """
        try:
            session_id_str = str(self.session_id)

            if event.type == "transcription":
                # User speech transcription
                text = event.data.get("text", "")
                if text:
                    context_sharing_service.add_event(
                        session_id_str,
                        ContextEvent(
                            event_type=ContextEventType.MESSAGE_SENT,
                            channel=ChannelType.VOICE,
                            session_id=session_id_str,
                            data={"role": "user", "content": text}
                        )
                    )

            elif event.type == "text.output":
                # AI assistant text output
                text = event.data.get("text", "")
                if text:
                    context_sharing_service.add_event(
                        session_id_str,
                        ContextEvent(
                            event_type=ContextEventType.MESSAGE_SENT,
                            channel=ChannelType.VOICE,
                            session_id=session_id_str,
                            data={"role": "assistant", "content": text}
                        )
                    )

            elif event.type == "intent":
                # Detected intent
                intent = event.data.get("intent")
                if intent:
                    context_sharing_service.add_event(
                        session_id_str,
                        ContextEvent(
                            event_type=ContextEventType.INTENT_DETECTED,
                            channel=ChannelType.VOICE,
                            session_id=session_id_str,
                            data=event.data
                        )
                    )

            elif event.type == "sentiment":
                # Analyzed sentiment
                sentiment = event.data.get("sentiment")
                if sentiment:
                    context_sharing_service.add_event(
                        session_id_str,
                        ContextEvent(
                            event_type=ContextEventType.SENTIMENT_ANALYZED,
                            channel=ChannelType.VOICE,
                            session_id=session_id_str,
                            data=event.data
                        )
                    )

        except Exception as e:
            logger.warning(f"Failed to capture event for sharing in session {self.session_id}: {e}")

    async def _generate_ai_insights(self, message: str, role: str) -> None:
        """Generate AI insights for a message and send to client.
        
        Args:
            message: Message content
            role: Message role (user/assistant)
        """
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": role,
                "content": message,
                "timestamp": asyncio.get_event_loop().time()
            })

            # Only analyze user messages for insights
            if role != "user":
                return

            # Generate insights
            insights = await ai_insights_service.process_message(
                message=message,
                role=role,
                conversation_history=self.conversation_history
            )

            # Create and send insight events
            events = ai_insights_service.create_insight_events(insights)
            for event in events:
                await self.websocket.send_json(event)

        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")

    async def _handle_suggestion_action(self, data: dict[str, Any]) -> None:
        """Handle suggestion action from client.
        
        Args:
            data: Suggestion action data
        """
        try:
            suggestion_id = data.get("suggestionId")
            action = data.get("action")
            suggestion = data.get("suggestion")

            logger.info(f"Suggestion {action}: {suggestion_id} - {suggestion}")

            # Here you could:
            # 1. Log the action to database
            # 2. Execute automated actions if accepted
            # 3. Update analytics
            # 4. Send confirmation back to client

            # Send confirmation
            await self.websocket.send_json({
                "type": "suggestion-action-confirmed",
                "suggestionId": suggestion_id,
                "action": action,
                "timestamp": asyncio.get_event_loop().time()
            })

        except Exception as e:
            logger.error(f"Error handling suggestion action: {e}")

    async def _send_error(self, error: str) -> None:
        """Send error message to client.

        Args:
            error: Error message
        """
        try:
            await self.websocket.send_json({
                "type": "error",
                "error": error,
            })
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    @staticmethod
    def _twilio_media_to_chunk(media: dict[str, Any]) -> AudioChunk | None:
        """Convert Twilio media payload to AudioChunk.

        Args:
            media: Media dictionary from Twilio event

        Returns:
            AudioChunk or None if payload invalid
        """

        payload = media.get("payload")
        if not payload:
            return None

        try:
            audio_bytes = base64.b64decode(payload)
        except (ValueError, TypeError) as exc:
            logger.error("Failed to decode Twilio audio payload: %s", exc)
            return None

        sample_rate_raw = media.get("sampleRate") or media.get("sample_rate")
        try:
            sample_rate = int(sample_rate_raw) if sample_rate_raw else 16000
        except (TypeError, ValueError):
            sample_rate = 16000

        timestamp_raw = media.get("timestamp")
        try:
            timestamp = float(timestamp_raw) / 1000.0 if timestamp_raw is not None else None
        except (TypeError, ValueError):
            timestamp = None

        return AudioChunk(
            data=audio_bytes,
            format=AudioFormat.PCM16,
            sample_rate=sample_rate,
            timestamp=timestamp,
        )


async def create_websocket_handler(
    websocket: WebSocket, session_id: UUID
) -> WebSocketStreamHandler:
    """Factory function to create WebSocket handler.

    Args:
        websocket: FastAPI WebSocket connection
        session_id: Session identifier

    Returns:
        WebSocketStreamHandler: Handler instance
    """
    return WebSocketStreamHandler(websocket, session_id)
