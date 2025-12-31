"""Integration test for Gemini Live WebSocket connection.

Tests that the Gemini 2.0 Flash Experimental model supports real-time voice
via the bidiGenerateContent WebSocket endpoint.
"""

import asyncio
import json
import os
import pytest

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


def _skip_if_missing_api_key() -> None:
    if not GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not set")


@pytest.mark.asyncio
async def test_gemini_live_websocket_connection():
    """Test basic WebSocket connection to Gemini Live API."""
    _skip_if_missing_api_key()
    try:
        import websockets
    except ImportError:
        pytest.skip("websockets library not installed")

    url = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"

    try:
        async with websockets.connect(url, close_timeout=5) as ws:
            # Send setup message
            setup_msg = {
                "setup": {
                    "model": "models/gemini-2.0-flash-exp",
                    "generation_config": {
                        "temperature": 0.7,
                        "response_modalities": ["AUDIO"],
                        "speech_config": {
                            "voice_config": {"prebuilt_voice_config": {"voice_name": "Aoede"}}
                        },
                    },
                }
            }

            await ws.send(json.dumps(setup_msg))

            # Wait for setupComplete response
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            data = json.loads(response)

            assert "setupComplete" in data, f"Expected setupComplete, got: {data}"
            print(f"✓ Gemini Live connection successful: {data}")

    except Exception as e:
        pytest.fail(f"Failed to connect to Gemini Live: {e}")


@pytest.mark.asyncio
async def test_gemini_live_text_conversation():
    """Test text conversation via Gemini Live WebSocket."""
    _skip_if_missing_api_key()
    try:
        import websockets
    except ImportError:
        pytest.skip("websockets library not installed")

    url = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"

    try:
        async with websockets.connect(url, close_timeout=5) as ws:
            # Send setup message (text mode for simpler testing)
            setup_msg = {
                "setup": {
                    "model": "models/gemini-2.0-flash-exp",
                    "generation_config": {
                        "temperature": 0.7,
                        "response_modalities": ["TEXT"],
                    },
                }
            }

            await ws.send(json.dumps(setup_msg))

            # Wait for setupComplete
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            data = json.loads(response)
            assert "setupComplete" in data

            # Send a text message
            text_msg = {
                "clientContent": {
                    "turns": [
                        {
                            "role": "user",
                            "parts": [{"text": "Say 'hello' and nothing else."}],
                        }
                    ],
                    "turnComplete": True,
                }
            }

            await ws.send(json.dumps(text_msg))

            # Collect responses until turn complete
            responses = []
            while True:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=15.0)
                    data = json.loads(response)
                    responses.append(data)

                    # Check for turn complete
                    if "serverContent" in data:
                        if data["serverContent"].get("turnComplete"):
                            break

                except asyncio.TimeoutError:
                    break

            # Verify we got a response
            assert len(responses) > 0, "Expected at least one response"
            print(f"✓ Received {len(responses)} response(s) from Gemini Live")

            # Look for text in responses
            text_found = False
            for resp in responses:
                if "serverContent" in resp:
                    model_turn = resp["serverContent"].get("modelTurn", {})
                    parts = model_turn.get("parts", [])
                    for part in parts:
                        if "text" in part:
                            print(f"✓ Got text response: {part['text']}")
                            text_found = True

            assert text_found, "Expected text response from model"

    except Exception as e:
        pytest.fail(f"Failed text conversation with Gemini Live: {e}")


if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not set; skipping Gemini Live integration tests.")
    else:
        asyncio.run(test_gemini_live_websocket_connection())
        asyncio.run(test_gemini_live_text_conversation())
        print("All tests passed!")
