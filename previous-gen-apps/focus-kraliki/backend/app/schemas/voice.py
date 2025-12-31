from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any

from pydantic import BaseModel, Field


class VoiceProviderEnum(str, Enum):
    GEMINI_NATIVE = "gemini-native"
    OPENAI_REALTIME = "openai-realtime"
    DEEPGRAM_TRANSCRIPTION = "deepgram-transcription"


class InitVoiceSessionRequest(BaseModel):
    provider: VoiceProviderEnum = VoiceProviderEnum.GEMINI_NATIVE
    language: str = "en-US"
    voice: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VoiceTransportConfig(BaseModel):
    handshake: str
    protocol: str
    model: str
    iceServer: Optional[str] = None
    voice: Optional[str] = None


class InitVoiceSessionResponse(BaseModel):
    success: bool
    provider: VoiceProviderEnum
    sessionId: str
    expiresAt: datetime
    transport: VoiceTransportConfig
    metadata: Dict[str, Any]
    availableProviders: Dict[str, bool]


class ProcessVoiceInputRequest(BaseModel):
    audioData: str  # Base64 encoded audio
    mimetype: str = "audio/webm"
    language: str = "en"
    provider: Optional[VoiceProviderEnum] = None


class ProcessVoiceInputResponse(BaseModel):
    success: bool
    transcript: str
    response: str
    confidence: float = 0.95
    language: str
    provider: VoiceProviderEnum


class SynthesizeSpeechRequest(BaseModel):
    text: str
    provider: VoiceProviderEnum = VoiceProviderEnum.OPENAI_REALTIME
    voice: Optional[str] = None
    language: str = "en"
    format: str = "wav"


class SynthesizeSpeechResponse(BaseModel):
    success: bool
    audioData: str
    format: str
    duration: float
    provider: VoiceProviderEnum


class VoiceSessionStatusResponse(BaseModel):
    sessionId: str
    provider: VoiceProviderEnum
    status: str
    createdAt: datetime
    expiresAt: datetime
    transport: VoiceTransportConfig


class ChatWithAssistantRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    conversationId: Optional[str] = None


class ChatWithAssistantResponse(BaseModel):
    success: bool
    response: str
    conversationId: str
    confidence: float
    reasoning: Optional[str] = None


class VoiceProvidersResponse(BaseModel):
    providers: Dict[str, bool]


# Additional schemas for voice processing
class VoiceTranscribeRequest(BaseModel):
    language: str = "en"
    provider: Optional[str] = None


class VoiceTranscribeResponse(BaseModel):
    id: str
    transcript: str
    confidence: Optional[float] = None
    language: str
    duration: Optional[float] = None


class VoiceProcessRequest(BaseModel):
    transcript: str
    recordingId: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class VoiceProcessResponse(BaseModel):
    intent: str
    confidence: float
    entities: Dict[str, Any]
    response: str


class VoiceToTaskRequest(BaseModel):
    transcript: str
    recordingId: Optional[str] = None
    forceCreate: bool = False


class VoiceToTaskResponse(BaseModel):
    success: bool
    message: str
    task: Optional[Dict[str, Any]] = None
    confidence: float
