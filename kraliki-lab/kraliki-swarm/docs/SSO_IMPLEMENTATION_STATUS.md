# SSO Implementation Status - Kraliki Apps

**Date:** 2025-12-27
**Status:** Code Complete - Awaiting Zitadel Client Registration

## Overview

SSO (Single Sign-On) has been implemented across all Kraliki apps using Zitadel OIDC. Users can register once and access all apps with a single login.

## Apps Updated

| App | Path | Login Page | SSO Routes | Status |
|-----|------|------------|------------|--------|
| Focus by Kraliki | `/applications/focus-kraliki` | Updated with SSO button | `/auth/sso/*` | Code Complete |
| Voice by Kraliki | `/applications/voice-kraliki` | Updated with SSO button | `/auth/sso/*` | Code Complete |
| Speak by Kraliki | `/applications/speak-kraliki` | Updated with SSO button | `/auth/sso/*` | Code Complete |
| Learn by Kraliki | `/applications/learn-kraliki` | Updated with SSO button | `/auth/sso/*` | Code Complete |
| Kraliki Swarm | `/applications/kraliki-swarm/dashboard` | Already has SSO | `/auth/callback` | Reference Implementation |

## Files Created Per App

Each app received the following new files:

### 1. Server Auth Module
**Path:** `frontend/src/lib/server/auth.ts`

Contains:
- `isAuthConfigured()` - Check if Zitadel is configured
- `createAuthorizationURL(state)` - Generate OIDC authorize URL
- `validateAuthorizationCode(code)` - Exchange code for tokens
- `verifyIdToken(idToken)` - Verify JWT with JWKS
- `parseSessionCookie(cookie)` - Extract user from session

### 2. SSO Initiation Route
**Path:** `frontend/src/routes/auth/sso/+server.ts`

- Generates CSRF state
- Redirects to Zitadel authorize endpoint

### 3. SSO Callback Route
**Path:** `frontend/src/routes/auth/sso/callback/+server.ts`

- Validates CSRF state
- Exchanges code for tokens
- Verifies ID token
- Sets session cookie
- Redirects to dashboard

## Environment Variables Required

Each app needs these variables in `.env`:

```bash
# Zitadel Configuration
ZITADEL_DOMAIN=identity.verduona.dev
ZITADEL_CLIENT_ID=<from-zitadel>
ZITADEL_CLIENT_SECRET=<from-zitadel>

# Origin for OAuth callbacks (set per environment)
# Production: https://<app>.kraliki.com
# Beta/Dev: https://<app>.verduona.dev
ORIGIN=https://<app>.kraliki.com
```

## Next Steps - Zitadel Configuration

### 1. Create OIDC Applications in Zitadel

For each app, create a new Application in Zitadel:

1. Log into Zitadel Admin: https://identity.verduona.dev
2. Go to Projects > Default Project (or create new)
3. Click "New Application"
4. Select "Web Application"
5. Configure:
   - Name: `Focus by Kraliki` (or app name)
   - Type: Web
   - Authentication Method: Basic (client_secret_basic)
   - Redirect URIs:
     - `https://focus.kraliki.com/auth/sso/callback` (production)
     - `https://focus.verduona.dev/auth/sso/callback` (beta/dev)
     - `http://localhost:5173/auth/sso/callback` (local development)
6. Save and note the Client ID and Client Secret

### 2. Redirect URI Table

| App | Production Redirect URI | Beta/Dev Redirect URI | Local Redirect URI |
|-----|------------------------|------------------|
| Focus | `https://focus.kraliki.com/auth/sso/callback` | `https://focus.verduona.dev/auth/sso/callback` | `http://localhost:5173/auth/sso/callback` |
| Voice | `https://voice.kraliki.com/auth/sso/callback` | `https://voice.verduona.dev/auth/sso/callback` | `http://localhost:3000/auth/sso/callback` |
| Speak | `https://speak.kraliki.com/auth/sso/callback` | `https://speak.verduona.dev/auth/sso/callback` | `http://localhost:5175/auth/sso/callback` |
| Learn | `https://learn.kraliki.com/auth/sso/callback` | `https://learn.verduona.dev/auth/sso/callback` | `http://localhost:5173/auth/sso/callback` |

### 3. Update .env Files

After creating apps in Zitadel, update each app's `.env` with the credentials.

## Testing SSO Flow

1. Start the app locally
2. Navigate to login page
3. Click "Sign in with Kraliki SSO"
4. Should redirect to Zitadel login
5. After login, should redirect back to app dashboard

## Technical Details

### Session Storage

SSO sessions are stored in an HttpOnly cookie named `sso_session`:
- Expires: 7 days
- Secure: true (HTTPS only)
- SameSite: lax

### Token Verification

ID tokens are verified using:
- JWKS endpoint: `https://identity.verduona.dev/oauth/v2/keys`
- Issuer validation: `https://identity.verduona.dev`
- Library: `jose` (npm package)

### Dependencies Added

- `jose` - JWT/JWK library for token verification

## Security Considerations

1. **CSRF Protection**: State parameter prevents CSRF attacks
2. **Token Verification**: JWKS-based cryptographic verification
3. **Secure Cookies**: HttpOnly, Secure, SameSite=Lax
4. **Server-Side Only**: Auth logic runs on server, not client

## Fallback Authentication

Each app retains its original authentication method:
- Focus: Email/password + Google OAuth
- Voice: Email/password
- Speak: Email/password
- Learn: Dev token (temporary)

SSO is an additional option, not a replacement.

---

*Implementation by Claude Code - 2025-12-27*
