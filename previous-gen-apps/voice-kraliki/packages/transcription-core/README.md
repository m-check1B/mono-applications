# Transcription Core

Audio transcription services for Platform 2026.

## Providers

| Provider | Models | Use Case |
|----------|--------|----------|
| **Deepgram** | Nova-2, Whisper | Fast, accurate STT |

## Installation

```bash
pip install transcription-core[deepgram]
```

## Quick Start

```python
from transcription_core import DeepgramTranscriber, TranscriptionConfig

# Create transcriber
transcriber = DeepgramTranscriber(api_key="your-api-key")

# Transcribe file
with open("audio.wav", "rb") as f:
    result = await transcriber.transcribe_file(f.read())

print(result.text)
print(f"Confidence: {result.confidence}")
print(f"Duration: {result.duration}s")

# With configuration
config = TranscriptionConfig(
    model="nova-2",
    language="en",
    diarize=True,  # Speaker separation
    punctuate=True,
)
result = await transcriber.transcribe_file(audio_data, config)

# Word-level details
for word in result.words:
    print(f"{word.word} [{word.start:.2f}s - {word.end:.2f}s]")
```

## Transcribe from URL

```python
result = await transcriber.transcribe_url(
    "https://example.com/audio.mp3",
    config=TranscriptionConfig(model="whisper"),
)
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `model` | `nova-2` | Model (nova-2, whisper) |
| `language` | `en` | Language code |
| `punctuate` | `True` | Add punctuation |
| `diarize` | `False` | Speaker diarization |
| `smart_format` | `True` | Smart formatting |
| `utterances` | `False` | Split by utterance |
| `keywords` | `[]` | Keyword boosting |

## Supported Audio Formats

- WAV
- MP3
- FLAC
- OGG
- M4A
- WebM
