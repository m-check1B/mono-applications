"""Email service for sending verification and notification emails"""

import hashlib
import logging
import os
import secrets
import smtplib
from datetime import UTC, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email_validator import EmailNotValidError, validate_email

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending transactional emails"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@voice.kraliki.com")
        self.from_name = os.getenv("SMTP_FROM_NAME", "Voice by Kraliki")
        self.frontend_url = os.getenv("FRONTEND_URL", "https://voice.kraliki.com")

    def generate_verification_token(self) -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)

    def generate_verification_token_with_hash(self) -> tuple[str, str]:
        """Generate a secure verification token and its hash.

        Returns:
            Tuple of (plaintext_token, hashed_token)
            - plaintext_token: Send this to user via email
            - hashed_token: Store this in the database
        """
        plaintext_token = secrets.token_urlsafe(32)
        hashed_token = self.hash_token(plaintext_token)
        return plaintext_token, hashed_token

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token using SHA-256.

        Args:
            token: The plaintext token to hash

        Returns:
            Hex-encoded SHA-256 hash of the token
        """
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    def generate_token_expiration(self, hours: int = 24) -> datetime:
        """Generate token expiration datetime"""
        return datetime.now(UTC) + timedelta(hours=hours)

    def verify_email_address(self, email: str) -> bool:
        """Validate email address format"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    def _send_email(
        self, to_email: str, subject: str, html_content: str, text_content: str | None = None
    ) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_verification_email(
        self, to_email: str, token: str, user_name: str | None = None
    ) -> bool:
        """Send email verification email"""
        verification_url = f"{self.frontend_url}/verify-email?token={token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #6366f1; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{
                    display: inline-block;
                    background-color: #6366f1;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Voice by Kraliki</h1>
                </div>
                <div class="content">
                    <p>Hi{f" {user_name}" if user_name else ""},</p>
                    <p>Thank you for registering with Voice by Kraliki. Please verify your email address by clicking the button below:</p>
                    <p>
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #6366f1;">{verification_url}</p>
                    <p>This link will expire in 24 hours.</p>
                </div>
                <div class="footer">
                    <p>If you didn't create an account with Voice by Kraliki, you can safely ignore this email.</p>
                    <p>&copy; 2025 Voice by Kraliki</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to Voice by Kraliki!

        Hi{f" {user_name}" if user_name else ""},

        Thank you for registering with Voice by Kraliki. Please verify your email address by visiting:

        {verification_url}

        This link will expire in 24 hours.

        If you didn't create an account with Voice by Kraliki, you can safely ignore this email.

        © 2025 Voice by Kraliki
        """

        return self._send_email(
            to_email=to_email,
            subject="Verify Your Email Address",
            html_content=html_content,
            text_content=text_content,
        )

    def send_password_reset_email(
        self, to_email: str, token: str, user_name: str | None = None
    ) -> bool:
        """Send password reset email"""
        reset_url = f"{self.frontend_url}/reset-password?token={token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #6366f1; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{
                    display: inline-block;
                    background-color: #6366f1;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hi{f" {user_name}" if user_name else ""},</p>
                    <p>We received a request to reset your password for your Voice by Kraliki account.</p>
                    <p>Click the button below to reset your password:</p>
                    <p>
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #6366f1;">{reset_url}</p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request a password reset, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Voice by Kraliki</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request

        Hi{f" {user_name}" if user_name else ""},

        We received a request to reset your password for your Voice by Kraliki account.

        Visit the following link to reset your password:

        {reset_url}

        This link will expire in 1 hour.

        If you didn't request a password reset, you can safely ignore this email.

        © 2025 Voice by Kraliki
        """

        return self._send_email(
            to_email=to_email,
            subject="Reset Your Password",
            html_content=html_content,
            text_content=text_content,
        )


# Global email service instance
_email_service: EmailService | None = None


def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
