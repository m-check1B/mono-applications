# Human Task: Configure Google Login in Zitadel

**Priority:** Required for beta testing
**Estimated time:** 15 minutes

## What's Needed

Google login button appears on Zitadel's login page (not custom code). To enable it:

## Steps

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select/create project for MissionPerfect
3. Go to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth client ID**
5. Application type: **Web application**
6. Name: `Zitadel MissionPerfect`
7. Authorized redirect URIs:
   ```
   https://identity.missionperfect.cloud/ui/login/login/externalidp/callback
   ```
8. Save the **Client ID** and **Client Secret**

### 2. Configure in Zitadel

1. Login to Zitadel admin: https://identity.missionperfect.cloud/ui/console
2. Go to **Instance Settings > Identity Providers**
3. Click **Add Provider > Google**
4. Enter:
   - Client ID: (from step 1)
   - Client Secret: (from step 1)
   - Scopes: `openid email profile`
5. Enable: **Auto-register users**
6. Save

### 3. Enable for Login

1. Go to **Default Settings > Login Behavior and Access**
2. Under **Identity Providers**, enable Google
3. Save

## Verification

1. Go to any app login (e.g., focus-lite)
2. Should see "Continue with Google" button
3. Click and verify Google OAuth flow works

## Notes

- This is Zitadel configuration, not code
- auth-core package is already set up correctly for JWT validation
- Same process for Microsoft/Azure AD if needed later

---

*Created: 2024-12-09*
