# HW-012: Enable Vertex AI for Gemini Native Audio Models

**Created:** 2025-12-20
**Blocks:** VOICE-001, VOICE-003, VOICE-004
**Priority:** HIGH

## Problem

The Gemini 2.5 Flash Native Audio models (`gemini-2.5-flash-native-audio-preview-12-2025`) are **NOT available** via standard Gemini API keys.

**Verified 2025-12-20 15:25:** API query with existing key returns 50 models, but NO native audio models:
- `gemini-2.5-flash-native-audio-*` - NOT AVAILABLE
- `gemini-2.5-flash-preview-tts` - Available (TTS only, not bidirectional)
- `gemini-2.5-pro-preview-tts` - Available (TTS only, not bidirectional)

Native audio models require either:
1. **Vertex AI API** (Google Cloud Platform)
2. **Special access** granted by Google for preview features

## What's Needed

### Option A: Enable Vertex AI (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Enable the **Vertex AI API**
4. Create a Service Account:
   - IAM & Admin → Service Accounts → Create
   - Role: `Vertex AI User`
5. Download the JSON key file
6. Store in `/home/adminmatej/github/secrets/gcp-vertex-ai-key.json`
7. Set environment variable: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`

### Option B: Request API Access via AI Studio

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Check if native audio models appear in model selector
3. If not, look for "Request Access" or waitlist option
4. Some preview features require explicit opt-in

## Verification After Setup

```bash
# Test Vertex AI access
pip install google-cloud-aiplatform
python3 -c "
from google.cloud import aiplatform
aiplatform.init(project='YOUR_PROJECT_ID', location='us-central1')
# List available models
for model in aiplatform.Model.list():
    print(model.display_name)
"
```

## Code Already Complete

The voice integration code is ready and waiting:
- CC-Lite: `/home/adminmatej/github/applications/cc-lite-2026/`
- Voice of People: `/home/adminmatej/github/applications/voice-of-people/`
- Model ID: `gemini-2.5-flash-native-audio-preview-12-2025`
- Audio format: 16kHz PCM16 input, 24kHz PCM16 output

## Time Estimate

20-30 minutes (GCP console setup)

## Notes

- HW-010 was incorrectly marked DONE - the existing API key does NOT have native audio access
- Standard Gemini API keys only get TTS preview models, not bidirectional native audio
- Vertex AI is the official path for production native audio access

---
**Status:** PENDING
