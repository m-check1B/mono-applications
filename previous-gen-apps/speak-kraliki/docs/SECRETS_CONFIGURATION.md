# Speak by Kraliki - Secrets Configuration

This document describes how to configure API keys and secrets for production deployment.

## Quick Start

For local/dev, generate a `.env` with unique secrets:
```bash
./scripts/generate_env.sh
```

For production or CI, copy the example file:

1. Copy the example file:
   ```bash
   cp backend/.env.example .env
   ```

2. Edit `.env` with your production values

3. Start the application:
   ```bash
   docker compose up -d
   ```

## Required Secrets

These must be configured for the application to run:

### Database (PostgreSQL)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/speak` |
| `POSTGRES_USER` | DB username (docker-compose) | `speak_admin` |
| `POSTGRES_PASSWORD` | DB password (docker-compose) | `<strong random password>` |
| `POSTGRES_DB` | Database name | `speak` |

Generate a secure password:
```bash
openssl rand -base64 24
```

### Authentication (JWT)

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT signing key (min 32 chars) | `<generate securely>` |

Generate a secure JWT secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

### AI Services (Gemini)

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `GEMINI_API_KEY` | Google Gemini API key | [Google AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | Model to use | Default: `models/gemini-2.5-flash-native-audio-preview-12-2025` |

## Optional Secrets

Configure these based on features you need:

### Email (Resend)

For sending survey invitations and notifications.

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `RESEND_API_KEY` | Resend API key | [Resend API Keys](https://resend.com/api-keys) |
| `EMAIL_FROM` | Sender address | Must be verified domain |

### Payments (Stripe)

For subscription billing.

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `STRIPE_SECRET_KEY` | Stripe secret key | [Stripe Dashboard](https://dashboard.stripe.com/apikeys) |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | Stripe Webhook settings |
| `STRIPE_PRICE_PERSONAL` | Personal plan price ID | Stripe Products |
| `STRIPE_PRICE_PREMIUM` | Premium plan price ID | Stripe Products |
| `STRIPE_PRICE_PRO` | Pro plan price ID | Stripe Products |

### Telephony (Telnyx)

For voice call features.

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `TELNYX_API_KEY` | Telnyx API v2 key | [Telnyx Portal](https://portal.telnyx.com/) |
| `TELNYX_PUBLIC_KEY` | Public key for webhook validation | Telnyx Portal |
| `TELNYX_CONNECTION_ID` | TeXML app connection ID | Telnyx Connections |
| `TELNYX_PHONE_NUMBER` | Outbound caller ID (E.164) | e.g., `+12025551234` |

## Ed25519 JWT (Production Recommended)

For enhanced security in production, use Ed25519 instead of HS256:

```bash
# Generate Ed25519 key pair
python3 << 'EOF'
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

key = Ed25519PrivateKey.generate()
private = key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption()
)
public = key.public_key().public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo
)

print("ED25519_PRIVATE_KEY:")
print(private.decode())
print("\nED25519_PUBLIC_KEY:")
print(public.decode())
EOF
```

Then in `.env`:
```
USE_ED25519=true
ED25519_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMC4CAQAwBQ...
ED25519_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----\nMCowBQ...
```

## Security Best Practices

1. **Never commit `.env`** - It's in `.gitignore` for a reason
2. **Use unique secrets per environment** - Dev, staging, production each get their own
3. **Rotate secrets regularly** - Especially after team member departures
4. **Use secret managers in production** - Consider Vault, AWS Secrets Manager, etc.
5. **Test key validity** - After receiving API keys from providers
6. **Monitor API usage** - Set up billing alerts for paid services

## Validation

The application validates secrets on startup in production mode (`DEBUG=false`).

Check validation manually:
```bash
cd backend
source .venv/bin/activate
python3 -c "from app.core.auth import validate_production_security; validate_production_security()"
```

## Troubleshooting

### "JWT_SECRET_KEY is too short"
Generate a new key with at least 32 characters using the command above.

### "DATABASE_URL contains default credentials"
Update to a secure password - don't use `postgres:postgres`.

### "Stripe price IDs contain placeholders"
Create products in Stripe Dashboard and use real price IDs.

---

*Part of Speak by Kraliki - see [CLAUDE.md](../CLAUDE.md) for project details*
