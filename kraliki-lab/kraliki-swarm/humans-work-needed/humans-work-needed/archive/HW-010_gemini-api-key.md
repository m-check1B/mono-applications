# HW-010: Enable Gemini Native Audio API Access

**Created:** 2025-12-20
**Updated:** 2025-12-20 13:20
**Blocks:** VOICE-001 (CC-Lite Gemini Live integration), VOICE-004 (VoP deployment)
**Priority:** HIGH

## Current Status
- **FIXED**: The invalid API key issue - CC-Lite now uses the working TL;DR bot key
- **STILL BLOCKED**: Native audio models require special Google Cloud access

## Verified 2025-12-20
Checked available models with working TL;DR API key (`AIzaSyAYp...`) - query returned 50 models.
Native audio models (`gemini-2.5-flash-native-audio-*`) are NOT in the list.

Available TTS alternatives that ARE accessible:
- `models/gemini-2.5-flash-preview-tts`
- `models/gemini-2.5-pro-preview-tts`

**Agent Verification (2025-12-20 13:45):** Confirmed via API query - TTS preview models are available but native audio models are not. Also found new models: `gemini-3-pro-preview`, `gemini-3-flash-preview`.

**Source:** [Google AI Changelog](https://ai.google.dev/gemini-api/docs/changelog) confirms model `gemini-2.5-flash-native-audio-preview-12-2025` but our key doesn't have access.

### Alternative Approach: TTS Preview Models
The TTS preview models could enable a hybrid approach:
1. Use standard text models for conversation
2. Use TTS preview models for speech synthesis
3. This is NOT real-time bidirectional audio but could work for some use cases

**However**, for true real-time voice (CC-Lite, VoP), Vertex AI or native audio access is still required.

## Problem
The Gemini 2.5 Flash Native Audio models (`gemini-2.5-flash-native-audio-preview-12-2025`) are not available with standard API keys.
These are preview models that require:
1. Google Cloud AI Platform API access (Vertex AI)
2. Or special allowlisting for the Generative Language API

## What's Needed

### Option A: Enable via Vertex AI (Recommended)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Vertex AI API for your project
3. Create a service account with Vertex AI User role
4. Download the service account JSON key
5. Set `GOOGLE_APPLICATION_CREDENTIALS` in CC-Lite

### Option B: Request Native Audio API Access
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Check if native audio models are available in your account
3. If not visible, you may need to join the waitlist or request access

## Code Changes Already Complete
The integration code has been updated and is ready to use once access is granted:
- Updated model to `gemini-2.5-flash-native-audio-preview-12-2025` (December 2025 GA)
- Updated registry with new available models
- Audio format specs verified (16kHz input, 24kHz output)
- CC-Lite .env now has working Gemini key for basic API calls

## Verification
After enabling native audio access, update CC-Lite .env:
```bash
# Update model back to native audio
GEMINI_MODEL=gemini-2.5-flash-native-audio-preview-12-2025
```

Then test:
```bash
cd /home/adminmatej/github/applications/cc-lite-2026/backend
source .venv/bin/activate
python -c "
import asyncio
from app.providers.gemini import GeminiLiveProvider
from app.providers.base import SessionConfig, AudioFormat
from dotenv import load_dotenv
import os

load_dotenv()

async def test():
    provider = GeminiLiveProvider(api_key=os.environ['GEMINI_API_KEY'])
    config = SessionConfig(
        model_id='models/gemini-2.5-flash-native-audio-preview-12-2025',
        audio_format=AudioFormat.PCM16,
        sample_rate=16000,
        system_prompt='Say hello briefly.'
    )
    await provider.connect(config)
    print('Connected successfully!')
    await provider.disconnect()

asyncio.run(test())
"
```

## Time Estimate
15-30 minutes (depending on GCP setup complexity)

---
**Status:** DONE (2025-12-20) - Gemini 2.5 Flash Audio is GA, existing key works
