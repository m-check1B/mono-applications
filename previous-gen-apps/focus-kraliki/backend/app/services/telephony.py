from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:
    from twilio.rest import Client as TwilioClient  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    TwilioClient = None

from vendor.telephony_core import (
    TelephonyProvider,
    TelephonyProviderUnavailable,
)


class TelnyxProvider:
    """Minimal Telnyx provider wrapper (patched in tests)."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def create_call(
        self,
        *,
        from_number: str,
        to_number: str,
        callback_url: str | None = None,
        metadata: dict | None = None,
    ):
        raise TelephonyProviderUnavailable("Telnyx provider not configured")

    async def send_sms(
        self,
        *,
        from_number: str,
        to_number: str,
        body: str,
    ):
        raise TelephonyProviderUnavailable("Telnyx provider not configured")


@dataclass(slots=True)
class TelephonyServiceConfig:
    twilio_account_sid: Optional[str]
    twilio_auth_token: Optional[str]
    telnyx_api_key: Optional[str]


class TelephonyService:
    def __init__(self, config: TelephonyServiceConfig) -> None:
        self._config = config

    def available_providers(self) -> dict[str, bool]:
        return {
            "twilio": bool(self._config.twilio_account_sid and self._config.twilio_auth_token),
            "telnyx": bool(self._config.telnyx_api_key),
        }

    async def create_call(
        self,
        *,
        provider: TelephonyProvider,
        from_number: str,
        to_number: str,
        callback_url: str | None = None,
        metadata: dict | None = None,
    ):
        if provider.value == "twilio":
            if not (self._config.twilio_account_sid and self._config.twilio_auth_token):
                raise TelephonyProviderUnavailable("Twilio provider not configured")
            if TwilioClient is None:
                raise TelephonyProviderUnavailable("Twilio SDK not installed")
            client = TwilioClient(self._config.twilio_account_sid, self._config.twilio_auth_token)
            return client.calls.create(
                to=to_number,
                from_=from_number,
                url=callback_url,
            )

        if provider.value == "telnyx":
            if not self._config.telnyx_api_key:
                raise TelephonyProviderUnavailable("Telnyx provider not configured")
            provider_client = TelnyxProvider(api_key=self._config.telnyx_api_key)
            return await provider_client.create_call(
                from_number=from_number,
                to_number=to_number,
                callback_url=callback_url,
                metadata=metadata,
            )

        raise TelephonyProviderUnavailable("Unsupported telephony provider")

    async def send_sms(
        self,
        *,
        provider: TelephonyProvider,
        from_number: str,
        to_number: str,
        body: str,
    ):
        if provider.value == "twilio":
            if not (self._config.twilio_account_sid and self._config.twilio_auth_token):
                raise TelephonyProviderUnavailable("Twilio provider not configured")
            if TwilioClient is None:
                raise TelephonyProviderUnavailable("Twilio SDK not installed")
            client = TwilioClient(self._config.twilio_account_sid, self._config.twilio_auth_token)
            return client.messages.create(
                to=to_number,
                from_=from_number,
                body=body,
            )

        if provider.value == "telnyx":
            if not self._config.telnyx_api_key:
                raise TelephonyProviderUnavailable("Telnyx provider not configured")
            provider_client = TelnyxProvider(api_key=self._config.telnyx_api_key)
            return await provider_client.send_sms(
                from_number=from_number,
                to_number=to_number,
                body=body,
            )

        raise TelephonyProviderUnavailable("Unsupported telephony provider")


__all__ = [
    "TelephonyService",
    "TelephonyServiceConfig",
    "TelephonyProvider",
    "TelephonyProviderUnavailable",
    "TelnyxProvider",
    "TwilioClient",
]
