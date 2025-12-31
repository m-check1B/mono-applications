# Google OAuth Setup for Focus by Kraliki Production

This guide explains how to configure Google OAuth credentials for Focus by Kraliki production deployment.

## Overview

Focus by Kraliki uses Google OAuth for user authentication and Google Calendar API integration. This requires setting up a Google Cloud Console project and configuring OAuth 2.0 credentials.

## Prerequisites

- Google Cloud account (free tier is sufficient)
- Focus by Kraliki production environment access
- Access to modify `docker-compose.prod.yml` and `.env` files

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project selector at the top
4. Click "New Project"
5. Enter project name (e.g., "focus-kraliki-production")
6. Click "Create"
7. Wait for project creation (1-2 minutes)
8. Select the newly created project

## Step 2: Enable Required APIs

1. Navigate to **APIs & Services** > **Library**
2. Search for and enable the following APIs:
   - **Google Calendar API** (for calendar integration)
   - **Google+ API** (for user profile information)

## Step 3: Configure OAuth Consent Screen

1. Navigate to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type
3. Click "Create"
4. Fill in the required information:
   - **App name**: Focus by Kraliki
   - **User support email**: your-email@yourdomain.com
   - **Developer contact information**: your-email@yourdomain.com
5. Click "Save and Continue"
6. Skip the "Scopes" section (click "Save and Continue")
7. Add test users (optional for testing)
8. Click "Save and Continue"
9. Click "Back to Dashboard"

## Step 4: Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services** > **Credentials**
2. Click "+ Create Credentials" > **OAuth client ID**
3. Select **Web application** as application type
4. Fill in the form:
   - **Name**: Focus by Kraliki Production
   - **Authorized JavaScript origins**:
     - `https://your-domain.com`
     - `https://app.yourdomain.com`
   - **Authorized redirect URIs**:
     - `https://api.yourdomain.com/auth/google/callback`
     - `https://your-domain.com/auth/google/callback`
5. Click "Create"
6. Copy the **Client ID** and **Client Secret** (you won't see the secret again!)

## Step 5: Configure Environment Variables

Add the credentials to your production environment file:

```bash
# Edit your production .env file
nano /home/adminmatej/github/applications/focus-kraliki/.env
```

Add these variables:

```bash
# Google OAuth Credentials
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
GOOGLE_CALENDAR_WEBHOOK_TOKEN=generate-random-string
```

Generate a secure webhook token:

```bash
openssl rand -hex 32
```

## Step 6: Update Docker Compose (Already Done)

The `docker-compose.prod.yml` file has been updated to include Google OAuth environment variables. No changes are needed here.

## Step 7: Deploy to Production

1. Ensure the `.env` file is properly configured with the new credentials
2. Restart the backend service:

```bash
cd /home/adminmatej/github/applications/focus-kraliki
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

3. Check the logs to ensure OAuth credentials are loaded:

```bash
docker logs focus-kraliki-backend
```

## Step 8: Test OAuth Flow

1. Navigate to your Focus by Kraliki application
2. Click "Sign in with Google"
3. Complete the OAuth flow
4. Verify you're successfully authenticated
5. Test Google Calendar integration (if enabled)

## Security Best Practices

1. **Never commit credentials to version control**
   - Ensure `.env` is in `.gitignore`
   - Never push `.env` files to GitHub

2. **Use separate projects for dev and production**
   - Don't use the same OAuth credentials across environments

3. **Regularly rotate secrets**
   - Update `GOOGLE_CALENDAR_WEBHOOK_TOKEN` periodically
   - Monitor for unauthorized access

4. **Monitor usage in Google Cloud Console**
   - Set up usage alerts
   - Review API usage quotas

5. **Restrict API access**
   - Only enable the APIs you need
   - Set up API key restrictions if applicable

## Troubleshooting

### OAuth Flow Fails

- Check that the redirect URIs match exactly (including trailing slashes)
- Verify the consent screen is properly configured
- Ensure the domain is properly verified in Google Search Console

### Calendar API Returns 403

- Verify Google Calendar API is enabled
- Check that the OAuth scope includes calendar access
- Ensure the user has granted calendar permissions

### Credentials Not Loaded

- Check that `.env` file is in the correct directory
- Verify environment variables are correctly named
- Restart Docker containers after adding credentials

### Webhook Verification Fails

- Verify `GOOGLE_CALENDAR_WEBHOOK_TOKEN` is set
- Check that webhook URL is reachable from Google servers
- Ensure firewall rules allow Google's IP addresses

## Next Steps

After OAuth is configured:

1. Set up calendar sync webhooks (see `docs/CALENDAR_SYNC_SETUP.md`)
2. Configure webhook endpoint in API gateway
3. Test full authentication and calendar integration flow
4. Set up monitoring and alerting for OAuth errors

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Google Cloud Console](https://console.cloud.google.com/)

## Support

If you encounter issues:

1. Check the backend logs: `docker logs focus-kraliki-backend -f`
2. Review Google Cloud Console for API errors
3. Consult the Focus by Kraliki team for assistance
