"""
Speak by Kraliki - Email Service
Send survey invitations, notifications, and alerts
"""

import logging
from datetime import datetime
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Resend."""

    def __init__(self):
        self.api_key = settings.resend_api_key
        self.from_email = settings.email_from
        self._client = None

    @property
    def client(self):
        """Lazy initialize Resend client."""
        if self._client is None and self.api_key:
            import resend
            resend.api_key = self.api_key
            self._client = resend
        return self._client

    async def send_survey_invitation(
        self,
        to_email: str,
        employee_name: str,
        company_name: str,
        magic_link: str,
        survey_name: str
    ) -> bool:
        """Send survey invitation email to employee."""
        subject = f"{company_name} - Tvuj mesicni check-in"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'JetBrains Mono', monospace; background: #050505; color: #F0F0F0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .card {{ background: #1a1a1a; border: 2px solid #F0F0F0; padding: 24px; }}
                .btn {{ display: inline-block; background: #33FF00; color: #000; padding: 12px 24px; text-decoration: none; font-weight: bold; text-transform: uppercase; margin-top: 20px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h1 style="color: #33FF00; margin: 0 0 20px 0;">SPEAK BY KRALIKI</h1>
                    <p>Ahoj {employee_name},</p>
                    <p>Je cas na tvuj mesicni check-in ve firme <strong>{company_name}</strong>.</p>
                    <p>Rozhovor trva cca 5 minut a je <strong>100% anonymni</strong>.</p>
                    <p>Tvuj nadrizeny neuvidí, co jsi rekl/a - vedeni dostane pouze agregovane vysledky.</p>
                    <a href="{magic_link}" class="btn">ZACIT ROZHOVOR</a>
                    <p class="footer">
                        Odkaz je platny 7 dni.<br>
                        Pokud nechces odpovidat, muzes tento email ignorovat.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self._send_email(to_email, subject, html)

    async def send_alert_notification(
        self,
        to_email: str,
        user_name: str,
        alert_type: str,
        alert_description: str,
        department_name: Optional[str],
        dashboard_link: str
    ) -> bool:
        """Send alert notification to HR/CEO."""
        subject = f"[ALERT] {alert_type.replace('_', ' ').title()} - Speak by Kraliki"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'JetBrains Mono', monospace; background: #050505; color: #F0F0F0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .card {{ background: #1a1a1a; border: 2px solid #FF3333; padding: 24px; }}
                .alert-type {{ color: #FF3333; font-weight: bold; text-transform: uppercase; }}
                .btn {{ display: inline-block; background: #33FF00; color: #000; padding: 12px 24px; text-decoration: none; font-weight: bold; text-transform: uppercase; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <p class="alert-type">! ALERT: {alert_type.replace('_', ' ').upper()}</p>
                    <p>Ahoj {user_name},</p>
                    <p>Byl detekovan novy alert ve Speak by Kraliki:</p>
                    <p><strong>{alert_description}</strong></p>
                    {"<p>Oddeleni: " + department_name + "</p>" if department_name else ""}
                    <a href="{dashboard_link}" class="btn">ZOBRAZIT DETAIL</a>
                </div>
            </div>
        </body>
        </html>
        """

        return await self._send_email(to_email, subject, html)

    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        company_name: str,
        login_link: str
    ) -> bool:
        """Send welcome email to new user."""
        subject = f"Vitejte ve Speak by Kraliki - {company_name}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'JetBrains Mono', monospace; background: #050505; color: #F0F0F0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .card {{ background: #1a1a1a; border: 2px solid #F0F0F0; padding: 24px; }}
                .btn {{ display: inline-block; background: #33FF00; color: #000; padding: 12px 24px; text-decoration: none; font-weight: bold; text-transform: uppercase; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h1 style="color: #33FF00; margin: 0 0 20px 0;">VITEJTE</h1>
                    <p>Ahoj {user_name},</p>
                    <p>Vas ucet pro <strong>{company_name}</strong> byl vytvoren.</p>
                    <p>Speak by Kraliki vam pomuze zjistit, co si vasi zamestnanci opravdu mysli.</p>
                    <a href="{login_link}" class="btn">PRIHLASIT SE</a>
                </div>
            </div>
        </body>
        </html>
        """

        return await self._send_email(to_email, subject, html)

    async def _send_email(self, to: str, subject: str, html: str) -> bool:
        """Send email via Resend API."""
        if not self.client:
            logger.debug(f"[EMAIL] Would send to {to}: {subject}")
            return True  # Fake success in dev mode

        try:
            self.client.Emails.send({
                "from": self.from_email,
                "to": to,
                "subject": subject,
                "html": html,
            })
            return True
        except Exception as e:
            logger.exception(f"[EMAIL] Error sending to {to}: {e}")
            return False
