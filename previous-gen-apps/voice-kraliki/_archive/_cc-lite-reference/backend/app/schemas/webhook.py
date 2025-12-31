"""Webhook schemas - Pydantic models for webhook payloads"""

from pydantic import BaseModel, Field
from typing import Optional, Any


class TwilioCallStatusWebhook(BaseModel):
    """Twilio call status webhook payload"""
    CallSid: str
    CallStatus: str  # initiated, ringing, answered, completed, busy, no-answer, failed
    From: str
    To: str
    CallDuration: Optional[str] = None
    Direction: Optional[str] = None
    ApiVersion: Optional[str] = None
    AccountSid: Optional[str] = None


class TwilioRecordingWebhook(BaseModel):
    """Twilio recording webhook payload"""
    RecordingSid: str
    RecordingUrl: str
    RecordingStatus: str  # completed, failed
    RecordingDuration: str
    CallSid: str
    AccountSid: Optional[str] = None
    ApiVersion: Optional[str] = None


class TwilioTranscriptionWebhook(BaseModel):
    """Twilio transcription webhook payload"""
    TranscriptionSid: str
    TranscriptionText: str
    TranscriptionStatus: str
    RecordingSid: str
    CallSid: str
    AccountSid: Optional[str] = None
    ApiVersion: Optional[str] = None


class IVRInputWebhook(BaseModel):
    """IVR input webhook payload"""
    CallSid: str
    From: str
    To: str
    Digits: Optional[str] = None
    SpeechResult: Optional[str] = None
    Confidence: Optional[str] = None


class WebhookResponse(BaseModel):
    """Standard webhook response"""
    success: bool
    message: str
    data: Optional[dict[str, Any]] = None
