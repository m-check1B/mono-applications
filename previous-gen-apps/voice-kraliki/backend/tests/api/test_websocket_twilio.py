"""Unit tests for Twilio media decoding."""

import base64

from app.streaming.websocket import WebSocketStreamHandler
from app.providers.base import AudioFormat


def test_twilio_media_to_chunk_decodes_payload():
    raw_audio = b"abcd" * 10
    payload = base64.b64encode(raw_audio).decode('utf-8')

    media = {
        "payload": payload,
        "sampleRate": "8000",
        "timestamp": 123456,
    }

    chunk = WebSocketStreamHandler._twilio_media_to_chunk(media)
    assert chunk is not None
    assert chunk.data == raw_audio
    assert chunk.format == AudioFormat.PCM16
    assert chunk.sample_rate == 8000
    assert chunk.timestamp == 123.456


def test_twilio_media_to_chunk_handles_invalid_base64():
    media = {"payload": "!!!invalid!!!"}
    chunk = WebSocketStreamHandler._twilio_media_to_chunk(media)
    assert chunk is None
