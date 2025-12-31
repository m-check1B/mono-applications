# Voice by Kraliki Credentials Setup Guide

## 🔐 Complete Credential Configuration

This guide provides instructions for obtaining and configuring all required credentials for Voice by Kraliki production deployment.

## 📋 Quick Reference Checklist

- [ ] Database credentials configured
- [ ] Redis password set
- [ ] All JWT secrets generated
- [ ] Twilio credentials (for voice calls)
- [ ] OpenAI API key (for AI features)
- [ ] Deepgram API key (for transcription)
- [ ] Gemini API key (for multimodal AI)
- [ ] Stripe keys (for payments)
- [ ] Sentry DSN (for error tracking)
- [ ] Google OAuth (optional)

---

## 1. 🔑 Generate Security Secrets

### Auto-Generate All Secrets

```bash
cd /home/adminmatej/github/apps/cc-lite
pnpm run secrets:generate
```

This generates and updates `.env.production` with:
- JWT_SECRET
- JWT_REFRESH_SECRET
- COOKIE_SECRET
- SESSION_SECRET
- SESSION_ENCRYPTION_KEY
- CSRF_SECRET
- WEBHOOK_SECRET

### Manual Generation (if needed)

```bash
# Generate 32-byte base64 secrets
openssl rand -base64 32

# Generate 16-byte hex secrets
openssl rand -hex 16

# Generate Ed25519 key pair (for auth tokens)
ssh-keygen -t ed25519 -f ./cc-lite-auth-key -N ""
# Private key: cc-lite-auth-key
# Public key: cc-lite-auth-key.pub
```

Add to `.env.production`:
```bash
JWT_SECRET=<generated-secret>
JWT_REFRESH_SECRET=<generated-secret>
COOKIE_SECRET=<generated-secret>
SESSION_SECRET=<generated-secret>
SESSION_ENCRYPTION_KEY=<generated-secret>
CSRF_SECRET=<generated-secret>
AUTH_PRIVATE_KEY=<content-of-cc-lite-auth-key>
AUTH_PUBLIC_KEY=<content-of-cc-lite-auth-key.pub>
```

---

## 2. 🗄️ Database Configuration

### PostgreSQL Setup

#### Option A: Use Docker (Recommended)
Docker Compose automatically sets up PostgreSQL. You just need to:

1. Set a strong password:
```bash
openssl rand -base64 24
```

2. Update `.env.production`:
```bash
DATABASE_URL=postgresql://cc_lite_user:<YOUR_PASSWORD>@postgres:5432/cc_light_prod
```

#### Option B: External PostgreSQL
```bash
# Format
DATABASE_URL=postgresql://username:password@host:port/database

# Example
DATABASE_URL=postgresql://cc_user:SuperSecret123!@db.example.com:5432/cc_lite_prod
```

### Test Database Connection
```bash
# If using Docker
docker exec -it cc-lite-postgres-prod psql -U cc_lite_user -d cc_light_prod

# If external
psql "$DATABASE_URL" -c "SELECT version();"
```

---

## 3. 🔴 Redis Configuration

### Redis Password

1. Generate password:
```bash
openssl rand -base64 24
```

2. Update `.env.production`:
```bash
REDIS_PASSWORD=<generated-password>
REDIS_URL=redis://:<generated-password>@redis:6379
```

### Test Redis Connection
```bash
# If using Docker
docker exec -it cc-lite-redis-prod redis-cli AUTH <password> PING

# Should return: PONG
```

---

## 4. 📞 Twilio Setup (Voice Calls)

### Get Twilio Credentials

1. **Sign up**: https://www.twilio.com/try-twilio
2. **Get free trial** ($15 credit)
3. **Locate credentials** in Console Dashboard

### Required Values

Navigate to: **Console Dashboard** → **Account Info**

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
```

### Get Phone Number

Navigate to: **Phone Numbers** → **Buy a Number**

1. Choose country
2. Filter by capabilities (Voice, SMS)
3. Purchase number
4. Copy number in E.164 format (+1234567890)

```bash
TWILIO_PHONE_NUMBER=+1234567890
```

### Configure Webhooks

In Twilio Console → **Phone Numbers** → **Active Numbers** → Select your number:

**Voice Configuration**:
- A CALL COMES IN: `https://beta.cc-lite.yourdomain.com/api/twilio/voice`
- Method: `HTTP POST`

**Status Callbacks**:
- Status Callback URL: `https://beta.cc-lite.yourdomain.com/api/twilio/status`

### Test Twilio Integration
```bash
# Test outbound call
curl -X POST http://localhost:3010/api/calls/test-outbound \
  -H "Content-Type: application/json" \
  -d '{"to": "+1234567890", "message": "Test call"}'
```

---

## 5. 🤖 OpenAI API Key (AI Features)

### Get OpenAI API Key

1. **Sign up**: https://platform.openai.com/signup
2. **Navigate to**: https://platform.openai.com/api-keys
3. **Create new key**: Click "Create new secret key"
4. **Copy key**: `sk-...` (save immediately, won't be shown again)

### Pricing (as of 2024)
- **GPT-4o-mini**: $0.15/1M input tokens, $0.60/1M output tokens
- **GPT-4o**: $5/1M input tokens, $15/1M output tokens
- **Realtime API**: $0.06/minute (input), $0.24/minute (output)

### Configure
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_REALTIME_MODEL=gpt-4o-mini-realtime-preview-2024-12-17
OPENAI_DEFAULT_VOICE=nova
```

### Test
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 6. 🎙️ Deepgram API Key (Transcription)

### Get Deepgram API Key

1. **Sign up**: https://console.deepgram.com/signup
2. **Free tier**: $200 credit
3. **Create API Key**: Console → API Keys → Create New Key
4. **Copy key**

### Configure
```bash
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPGRAM_DEFAULT_VOICE=asteria-en
```

### Test
```bash
curl -X GET 'https://api.deepgram.com/v1/keys' \
  -H "Authorization: Token $DEEPGRAM_API_KEY"
```

---

## 7. 🌟 Google Gemini API Key (Multimodal AI)

### Get Gemini API Key

1. **Navigate to**: https://makersuite.google.com/app/apikey
2. **Sign in** with Google account
3. **Create API Key**
4. **Copy key**

### Pricing
- **Gemini 2.0 Flash**: FREE up to 1500 RPM
- **Gemini 2.5 Pro**: Paid tier

### Configure
```bash
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-2.5-flash-exp
GEMINI_DEFAULT_VOICE=Kore
```

### Test
```bash
curl "https://generativelanguage.googleapis.com/v1/models?key=$GEMINI_API_KEY"
```

---

## 8. 💳 Stripe Setup (Payments)

### Get Stripe Keys

1. **Sign up**: https://dashboard.stripe.com/register
2. **Navigate to**: Developers → API Keys
3. **Copy keys**:
   - **Publishable key**: `pk_test_...` (for frontend)
   - **Secret key**: `sk_test_...` (for backend)

### Configure
```bash
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Webhook Secret

1. **Navigate to**: Developers → Webhooks
2. **Add endpoint**: `https://beta.cc-lite.yourdomain.com/api/payments/webhook`
3. **Select events**: `payment_intent.*`, `customer.*`
4. **Copy signing secret**

```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Test Mode
```bash
# Use test mode initially
PAYMENT_MOCK_MODE=false
STRIPE_SECRET_KEY=sk_test_... # Use test key
```

---

## 9. 🐞 Sentry Setup (Error Tracking)

### Get Sentry DSN

1. **Sign up**: https://sentry.io/signup/
2. **Create project**: Select "Node.js"
3. **Copy DSN**: Settings → Client Keys (DSN)

### Configure
```bash
SENTRY_DSN=https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxx@sentry.io/xxxxxxx
```

### Test
```bash
# Sentry will automatically capture errors
# Or send test event
curl -X POST http://localhost:3010/api/sentry/test
```

---

## 10. 🔐 Google OAuth (Optional)

### Setup Google OAuth

1. **Navigate to**: https://console.cloud.google.com/
2. **Create project**: "Voice by Kraliki Production"
3. **Enable API**: APIs & Services → Enable APIs → Google+ API
4. **Create credentials**: Credentials → Create OAuth 2.0 Client ID
5. **Application type**: Web application
6. **Authorized redirect URIs**:
   ```
   https://beta.cc-lite.yourdomain.com/api/auth/google/callback
   ```

### Configure
```bash
GOOGLE_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_REDIRECT_URI=https://beta.cc-lite.yourdomain.com/api/auth/google/callback
```

---

## 11. 📊 Optional Services

### Anthropic Claude API
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
Get key: https://console.anthropic.com/

### AWS S3 (for recording storage)
```bash
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
S3_RECORDING_BUCKET=cc-lite-recordings
S3_RECORDING_REGION=us-east-1
```
Setup: https://console.aws.amazon.com/iam/

### SMTP (for emails)
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=app-specific-password
SMTP_FROM=noreply@yourdomain.com
```

---

## 🔒 Security Best Practices

### 1. Never Commit Secrets
```bash
# Always in .gitignore
.env
.env.production
.env.local
secrets/
```

### 2. Use Strong Passwords
- Minimum 32 characters for secrets
- Use `openssl rand -base64 32`
- Never reuse passwords

### 3. Rotate Secrets Regularly
```bash
# Rotate every 90 days
pnpm run secrets:rotate
```

### 4. Use Docker Secrets in Production
```bash
# Create secrets
echo "$JWT_SECRET" | docker secret create cc_lite_jwt_secret -

# Use in infra/docker/production.yml
secrets:
  cc_lite_jwt_secret:
    external: true
```

### 5. Restrict Access
- Use environment-specific keys (test vs production)
- Enable MFA on all service accounts
- Use least-privilege IAM policies

---

## ✅ Verification Checklist

Run this script to verify all credentials:

```bash
bash deploy/scripts/verify-credentials.sh
```

Or manually check:

```bash
# Check environment file
grep -c "CHANGE_ME" .env.production
# Should return: 0

# Test database
psql "$DATABASE_URL" -c "SELECT 1;"

# Test Redis
redis-cli -h redis PING

# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Twilio
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

---

## 🆘 Troubleshooting

### "Invalid JWT Secret"
- Ensure JWT_SECRET is exactly 32 characters (base64)
- No trailing spaces or newlines

### "Database Connection Failed"
- Verify DATABASE_URL format
- Check PostgreSQL is running
- Test with `psql` command

### "Twilio Authentication Failed"
- Verify Account SID starts with "AC"
- Check Auth Token for typos
- Ensure webhook URLs are publicly accessible

### "OpenAI Rate Limit"
- Check usage: https://platform.openai.com/usage
- Add payment method if on free tier
- Use GPT-4o-mini for lower costs

---

## 📞 Support

Need help? Contact:
- **Email**: support@yourdomain.com
- **Docs**: `/docs`
- **Issues**: GitHub Issues

---

**Last Updated**: 2025-01-29