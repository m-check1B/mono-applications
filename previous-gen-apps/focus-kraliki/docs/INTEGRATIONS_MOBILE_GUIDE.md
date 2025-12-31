# Focus by Kraliki - Integrations & Mobile Guide

**Track 6 Implementation - Complete**
**Author:** II-Agent Integration Specialist
**Date:** 2025-11-16
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Invoice & Billable Hours Export](#invoice--billable-hours-export)
3. [Google Calendar Two-Way Sync](#google-calendar-two-way-sync)
4. [Progressive Web App (PWA)](#progressive-web-app-pwa)
5. [Offline Mode](#offline-mode)
6. [II-Agent Integration Tools](#ii-agent-integration-tools)
7. [API Reference](#api-reference)
8. [Use Cases & Examples](#use-cases--examples)

---

## Overview

Focus by Kraliki now includes comprehensive integrations and mobile capabilities designed specifically for freelancers, remote workers, and teams who need productivity on-the-go.

### Key Features

- **Invoice Export** - Generate professional invoices from tracked time
- **Google Calendar Sync** - Two-way sync between tasks and calendar events
- **PWA Support** - Install as native app on mobile and desktop
- **Offline Mode** - Full offline functionality with background sync
- **II-Agent Tools** - AI agent can manage integrations autonomously

### Persona Alignment

These features address critical needs from our user research:

- **Freelancers (Maria)** - CR-001: Invoice generation with billable hours
- **All Segments** - CR-002: Google Calendar two-way sync
- **Mobile Users** - CR-003: PWA with offline support

---

## Invoice & Billable Hours Export

### Overview

Freelancers can export tracked time as professional invoices in CSV or JSON format, with automatic calculations, project breakdowns, and client customization.

### Features

- Generate invoices from time entries
- Filter by date range and project
- Automatic billable/non-billable separation
- Project-level breakdowns
- Custom hourly rates
- CSV and JSON export formats
- Weekly and monthly summaries

### API Endpoints

#### Generate Invoice

```http
POST /exports/invoices/generate
```

**Request Body:**
```json
{
  "start_date": "2025-11-01",
  "end_date": "2025-11-30",
  "client_name": "Acme Corp",
  "invoice_number": "INV-2025-001",
  "hourly_rate": 75.00,
  "format": "csv",
  "project_id": "optional-project-id",
  "include_non_billable": false
}
```

**Response (JSON format):**
```json
{
  "invoice": {
    "invoice_number": "INV-2025-001",
    "client_name": "Acme Corp",
    "invoice_date": "2025-11-16",
    "period_start": "2025-11-01",
    "period_end": "2025-11-30",
    "freelancer": {
      "name": "Maria Rodriguez",
      "email": "maria@example.com"
    }
  },
  "summary": {
    "total_hours": 120.5,
    "billable_hours": 108.0,
    "non_billable_hours": 12.5,
    "total_amount": 8100.00,
    "currency": "USD"
  },
  "projects": [
    {
      "project_name": "Website Redesign",
      "total_hours": 80.0,
      "total_amount": 6000.00,
      "entries": [...]
    }
  ]
}
```

#### Get Billable Summary

```http
GET /exports/billable/summary?start_date=2025-11-01&end_date=2025-11-30
```

**Response:**
```json
{
  "total_hours": 120.5,
  "billable_hours": 108.0,
  "non_billable_hours": 12.5,
  "total_amount": 8100.00,
  "currency": "USD",
  "projects": [
    {
      "project_id": "proj-123",
      "project_name": "Website Redesign",
      "total_hours": 80.0,
      "billable_hours": 75.0,
      "total_amount": 6000.00
    }
  ],
  "date_range": {
    "start": "2025-11-01",
    "end": "2025-11-30"
  }
}
```

#### Get Weekly Breakdown

```http
GET /exports/billable/weekly?weeks=4
```

Returns billable hours and revenue broken down by week.

### Usage Examples

#### Example 1: Monthly Invoice for Client

```bash
curl -X POST http://localhost:8000/exports/invoices/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-01",
    "end_date": "2025-11-30",
    "client_name": "Acme Corp",
    "invoice_number": "INV-2025-11",
    "hourly_rate": 75.00,
    "format": "csv"
  }'
```

#### Example 2: Quick Summary Check

```bash
curl -X GET "http://localhost:8000/exports/billable/summary?start_date=2025-11-01&end_date=2025-11-16" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### II-Agent Integration

The II-Agent can generate invoices on your behalf:

**User:** "Generate my invoice for November for Acme Corp"

**II-Agent:** Uses `export_invoice` tool to create invoice automatically.

---

## Google Calendar Two-Way Sync

### Overview

Seamlessly sync Focus by Kraliki tasks with Google Calendar events. Tasks with due dates appear in your calendar, and calendar events create corresponding tasks in Focus.

### Features

- **Two-way sync** - Changes sync both directions
- **OAuth 2.0 authentication** - Secure Google account connection
- **Background sync** - Automatic sync on schedule
- **Manual triggers** - Sync on-demand via API or UI
- **Conflict resolution** - Last-modified wins
- **Webhook support** - Real-time updates from Google

### Setup Process

#### Step 1: Initiate OAuth Flow

```http
POST /calendar-sync/oauth/init
```

**Request:**
```json
{
  "redirect_uri": "http://localhost:5173/calendar/callback"
}
```

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "csrf_token_abc123"
}
```

Redirect user to `auth_url` to authorize Google Calendar access.

#### Step 2: Exchange Authorization Code

After user authorizes, Google redirects back with a code. Exchange it for tokens:

```http
POST /calendar-sync/oauth/exchange
```

**Request:**
```json
{
  "code": "authorization_code_from_google",
  "redirect_uri": "http://localhost:5173/calendar/callback"
}
```

**Response:**
```json
{
  "access_token": "ya29.a0...",
  "refresh_token": "1//...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

Tokens are automatically stored in user preferences for future syncs.

### Sync Operations

#### Check Sync Status

```http
GET /calendar-sync/status
```

**Response:**
```json
{
  "enabled": true,
  "connected": true,
  "last_sync": "2025-11-16T10:30:00Z",
  "sync_direction": "two-way",
  "calendars": [
    {
      "id": "primary",
      "name": "Primary Calendar",
      "color": "#3B82F6"
    }
  ]
}
```

#### Trigger Manual Sync

```http
POST /calendar-sync/sync
```

**Request:**
```json
{
  "direction": "both",
  "start_date": "2025-11-01",
  "end_date": "2025-12-01"
}
```

**Sync Directions:**
- `to_calendar` - Push Focus tasks to Google Calendar
- `from_calendar` - Pull Google Calendar events to Focus
- `both` - Two-way sync (default)

#### Disconnect Calendar

```http
POST /calendar-sync/disconnect
```

Removes stored tokens and disables sync.

### How Sync Works

#### From Focus to Calendar

1. Query tasks with due dates in date range
2. Filter tasks not yet synced (no `google_calendar_id`)
3. Create calendar events via Google Calendar API
4. Store `google_calendar_id` on task for future updates

#### From Calendar to Focus

1. Fetch calendar events from Google Calendar API
2. Check for existing events by `google_calendar_id`
3. Create new Focus events for calendar items not yet synced
4. Link to tasks if applicable

#### Conflict Resolution

- **Last-modified wins** - If both sides changed, newest update takes precedence
- **Deletion handling** - Deleted items marked, not hard-deleted
- **Webhook updates** - Real-time changes from Google trigger immediate sync

### Webhook Setup (Real-Time Updates)

To enable real-time calendar updates (instead of polling), you need to register the webhook URL with Google Cloud Console. This is a one-time admin setup.

#### Prerequisites

1. Access to Google Cloud Console (console.cloud.google.com)
2. A GCP project (create one if needed)
3. Domain verification for `focus.verduona.dev`

#### Webhook URL

```
https://focus.verduona.dev/api/calendar-sync/webhook
```

#### Step 1: Create Google Cloud Project (if needed)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Name: `focus-kraliki-production` (or similar)
4. Click "Create"

#### Step 2: Enable Google Calendar API

1. Go to **APIs & Services** → **Library**
2. Search for "Google Calendar API"
3. Click **Enable**

#### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure OAuth consent screen first:
   - User Type: **External** (or Internal for Google Workspace)
   - App name: `Focus by Kraliki`
   - User support email: your email
   - Developer contact: your email
   - Scopes: Add `https://www.googleapis.com/auth/calendar.readonly` and `https://www.googleapis.com/auth/calendar.events`
   - Test users: Add your email for testing

4. Create OAuth client ID:
   - Application type: **Web application**
   - Name: `Focus by Kraliki Web`
   - Authorized JavaScript origins:
     - `https://focus.verduona.dev`
   - Authorized redirect URIs:
     - `https://focus.verduona.dev/calendar/callback`
     - `https://focus.verduona.dev/api/calendar-sync/oauth/callback`

5. Copy the **Client ID** and **Client Secret**

#### Step 4: Configure Environment Variables

Add to your `.env` file:

```bash
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
GOOGLE_CALENDAR_WEBHOOK_TOKEN=your_secure_random_token  # Optional: for extra security
```

Restart the backend service after updating `.env`.

#### Step 5: Verify Domain Ownership

For webhook registration, Google requires domain verification:

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Add property: `https://focus.verduona.dev`
3. Choose DNS verification method
4. Add the TXT record to your DNS provider (Cloudflare/Namecheap)
5. Verify ownership

#### Step 6: Register Push Notification Channel (via API)

Once OAuth is configured and users connect their calendars, the app will automatically set up push notification channels. The webhook receives notifications at:

```
POST https://focus.verduona.dev/api/calendar-sync/webhook
```

**Headers received from Google:**
- `X-Goog-Channel-ID`: Unique channel identifier
- `X-Goog-Resource-ID`: Calendar resource being watched
- `X-Goog-Resource-State`: `sync`, `exists`, or `not_exists`
- `X-Goog-Channel-Token`: Your verification token (if configured)

**Programmatic Channel Registration:**

The app registers watch channels when users connect. To manually register:

```python
# Example: Register watch channel via Google Calendar API
import httpx

async def watch_calendar(access_token: str, user_id: str, calendar_id: str = "primary"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/watch",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "id": f"user_{user_id}_calendar_{calendar_id}",
                "type": "web_hook",
                "address": "https://focus.verduona.dev/api/calendar-sync/webhook",
                "token": "your_verification_token",  # Optional
                "expiration": int((datetime.now() + timedelta(days=7)).timestamp() * 1000)
            }
        )
        return response.json()
```

**Note:** Watch channels expire (max 7 days). The app should renew them before expiration.

#### Step 7: Test the Integration

1. Connect Google Calendar in Focus by Kraliki UI
2. Create/modify an event in Google Calendar
3. Check backend logs for webhook receipt:
   ```
   INFO: Google Calendar webhook: channel=user_xxx_calendar_primary, state=exists
   ```
4. Verify the event appears in Focus by Kraliki

#### Webhook Security

The webhook endpoint validates:
- Required Google headers present
- Channel ID format matches expected pattern
- Optional token verification (if `GOOGLE_CALENDAR_WEBHOOK_TOKEN` set)

Invalid webhooks return 401/403 and are logged for security monitoring.

### II-Agent Integration

**User:** "Sync my tasks to Google Calendar"

**II-Agent:**
1. Checks sync status with `calendar_sync_status` tool
2. Triggers sync with `trigger_calendar_sync` tool
3. Reports success and sync details

---

## Progressive Web App (PWA)

### Overview

Focus by Kraliki can be installed as a native app on mobile and desktop devices, providing an app-like experience with offline support.

### Features

- **Install prompt** - One-click installation on supported devices
- **Standalone mode** - Runs in its own window (no browser chrome)
- **App shortcuts** - Quick access to key features from home screen
- **Share target** - Share content to Focus by Kraliki from other apps
- **Offline-first** - Full functionality without internet
- **Background sync** - Syncs when connection restored

### Manifest Configuration

Located at `/frontend/static/manifest.json`:

```json
{
  "name": "Focus by Kraliki",
  "short_name": "Focus",
  "description": "AI-powered planning and productivity system",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#667eea",
  "orientation": "portrait-primary",
  "categories": ["productivity", "business", "utilities"],
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "shortcuts": [
    {
      "name": "New Task",
      "url": "/dashboard/tasks",
      "icons": [{ "src": "/icon-192.png", "sizes": "192x192" }]
    },
    {
      "name": "Calendar",
      "url": "/dashboard/calendar",
      "icons": [{ "src": "/icon-192.png", "sizes": "192x192" }]
    },
    {
      "name": "Time Tracking",
      "url": "/dashboard/time",
      "icons": [{ "src": "/icon-192.png", "sizes": "192x192" }]
    }
  ],
  "share_target": {
    "action": "/share",
    "method": "POST",
    "enctype": "multipart/form-data",
    "params": {
      "title": "title",
      "text": "text",
      "url": "url"
    }
  }
}
```

### Service Worker

Located at `/frontend/static/service-worker.js`:

**Features:**
- Static asset caching
- Dynamic content caching
- Network-first for API calls
- Cache-first for assets
- Background sync support
- Push notifications

**Cache Strategy:**
```javascript
// API requests: Network first, cache fallback
if (request.url.includes('/api/')) {
  return networkFirst(request);
}

// Static assets: Cache first, network fallback
return cacheFirst(request);
```

### Installation

**Desktop (Chrome/Edge):**
1. Visit Focus by Kraliki in browser
2. Click install icon in address bar
3. Confirm installation
4. App opens in standalone window

**Mobile (iOS Safari):**
1. Open Focus by Kraliki in Safari
2. Tap Share button
3. Select "Add to Home Screen"
4. App appears on home screen

**Mobile (Android Chrome):**
1. Visit Focus by Kraliki in Chrome
2. Tap install banner when prompted
3. Confirm installation
4. App appears in app drawer

---

## Offline Mode

### Overview

Focus by Kraliki works completely offline using IndexedDB for local data storage and a background sync queue for pending operations.

### Architecture

**Storage Layer:**
- **IndexedDB** - Client-side database for tasks, projects, knowledge items
- **Sync Queue** - Pending operations queue for background sync
- **Service Worker** - Caches assets and handles offline requests

**Data Flow:**
1. User creates/updates item while offline
2. Item saved to IndexedDB immediately (instant UI update)
3. Operation queued for background sync
4. When online, background sync pushes changes to server
5. Server changes pulled and merged with local data

### IndexedDB Structure

**Stores:**
- `tasks` - Task items with status, due date indexes
- `projects` - Project items
- `knowledge` - Knowledge items with type indexes
- `timeEntries` - Time tracking entries
- `syncQueue` - Pending sync operations

**Implementation:**

Located at `/frontend/src/lib/utils/offlineStorage.ts`

### Usage Examples

#### Save Task Offline

```typescript
import { offlineTasks, queueOperation } from '$lib/utils/offlineStorage';

// Save task to IndexedDB
await offlineTasks.save({
  id: 'task-123',
  title: 'Review designs',
  status: 'PENDING',
  dueDate: '2025-11-17'
});

// Queue for sync when online
await queueOperation({
  type: 'create',
  entity: 'task',
  data: { title: 'Review designs', status: 'PENDING' },
  endpoint: '/tasks'
});
```

#### Get Offline Data

```typescript
// Get all tasks
const tasks = await offlineTasks.getAll();

// Get tasks by status
const pendingTasks = await offlineTasks.getByStatus('PENDING');

// Get specific task
const task = await offlineTasks.get('task-123');
```

#### Sync with Server

```typescript
import { syncWithServer } from '$lib/utils/offlineStorage';
import { api } from '$lib/api/client';

// Trigger manual sync
const result = await syncWithServer(api);

console.log(`Synced ${result.success} operations`);
console.log(`Failed ${result.failed} operations`);
```

### Service Worker Background Sync

The service worker automatically syncs when connection is restored:

```javascript
// In service worker
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-offline-data') {
    event.waitUntil(syncOfflineData());
  }
});
```

**Trigger from client:**
```javascript
// Register background sync
navigator.serviceWorker.ready.then((registration) => {
  registration.sync.register('sync-offline-data');
});
```

### Conflict Resolution

When syncing offline changes:

1. **No conflict** - Server accepts change directly
2. **Server newer** - Discard local change, keep server version
3. **Local newer** - Upload local change, update server
4. **Both changed** - Last-modified timestamp wins

---

## II-Agent Integration Tools

### Overview

The II-Agent can autonomously manage integrations using new Focus tools for invoices, calendar sync, and exports.

### Available Tools

#### 1. export_invoice

Generate invoice from billable hours.

**Usage:**
```python
result = await agent.use_tool('export_invoice', {
  'start_date': '2025-11-01',
  'end_date': '2025-11-30',
  'client_name': 'Acme Corp',
  'format': 'json'
})
```

#### 2. get_billable_summary

Get billable hours summary for date range.

**Usage:**
```python
result = await agent.use_tool('get_billable_summary', {
  'start_date': '2025-11-01',
  'end_date': '2025-11-16'
})
```

#### 3. calendar_sync_status

Check Google Calendar sync status.

**Usage:**
```python
result = await agent.use_tool('calendar_sync_status', {})
```

#### 4. trigger_calendar_sync

Manually trigger calendar sync.

**Usage:**
```python
result = await agent.use_tool('trigger_calendar_sync', {
  'direction': 'both',
  'start_date': '2025-11-01',
  'end_date': '2025-12-01'
})
```

### Example Workflows

#### Workflow 1: Monthly Invoice Generation

**User Request:** "Generate my November invoice for Acme Corp"

**II-Agent Execution:**
1. Get billable summary for November
2. Generate invoice with client details
3. Return summary and download link

#### Workflow 2: Weekly Review with Calendar Sync

**User Request:** "Review my week and sync calendar"

**II-Agent Execution:**
1. Get weekly billable summary
2. Check calendar sync status
3. Trigger calendar sync if needed
4. Summarize week and sync results

---

## API Reference

### Invoice & Export Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/exports/invoices/generate` | POST | Generate invoice from time entries |
| `/exports/billable/summary` | GET | Get billable hours summary |
| `/exports/billable/weekly` | GET | Get weekly billable breakdown |

### Calendar Sync Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/calendar-sync/oauth/init` | POST | Initialize OAuth flow |
| `/calendar-sync/oauth/exchange` | POST | Exchange code for tokens |
| `/calendar-sync/status` | GET | Get sync status |
| `/calendar-sync/sync` | POST | Trigger manual sync |
| `/calendar-sync/disconnect` | POST | Disconnect calendar |
| `/calendar-sync/webhook` | POST | Webhook for calendar updates |

### Time Tracking Endpoints (Existing)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/time-entries` | GET | List time entries |
| `/time-entries` | POST | Create time entry |
| `/time-entries/{id}` | GET | Get time entry |
| `/time-entries/{id}` | PATCH | Update time entry |
| `/time-entries/{id}/stop` | POST | Stop timer |
| `/time-entries/export/csv` | GET | Export to CSV |

---

## Use Cases & Examples

### Freelancer Invoice Workflow

**Persona:** Maria (Freelancer from 02-freelancer.md)

**Scenario:** End of month, Maria needs to invoice her clients.

**Steps:**
1. Open Focus by Kraliki dashboard
2. Navigate to Exports section
3. Select date range (November 1-30)
4. Choose client (Acme Corp)
5. Set hourly rate ($75/hr)
6. Generate invoice (CSV format)
7. Download and send to client via email

**Or via II-Agent:**

**Maria:** "Generate my November invoice for Acme Corp at $75/hour"

**II-Agent:**
```
Generated invoice for Acme Corp:
- Total Hours: 120.5
- Billable Hours: 108.0
- Total Amount: $8,100.00

Invoice INV-2025-11 ready for download.
```

### Calendar Sync for Remote Worker

**Scenario:** Sync weekly tasks to Google Calendar for visibility.

**Steps:**
1. Connect Google Calendar (one-time OAuth)
2. Set sync direction to "two-way"
3. Trigger manual sync for this week
4. Tasks with due dates appear in calendar
5. Calendar events create Focus tasks automatically

**Or via II-Agent:**

**User:** "Sync my tasks to Google Calendar for this week"

**II-Agent:**
```
Calendar sync triggered successfully!
Direction: both
Date Range: 2025-11-16 to 2025-11-23

Synced 12 tasks to calendar.
Created 3 tasks from calendar events.
```

### Mobile Offline Usage

**Scenario:** Working on plane without WiFi.

**Steps:**
1. Open Focus by Kraliki PWA (installed on phone)
2. Create new tasks (saved to IndexedDB)
3. Update existing tasks (queued for sync)
4. Start/stop time tracking (stored locally)
5. When landing and WiFi connects, background sync runs
6. All changes pushed to server automatically

**User sees:**
- "Offline mode - Changes will sync when online"
- Pending sync badge showing 5 queued operations
- After sync: "5 changes synced successfully"

---

## Best Practices

### Invoice Generation

1. **Set default hourly rate** in user settings for faster invoicing
2. **Use consistent invoice numbering** (e.g., INV-YYYY-MM-001)
3. **Review before sending** - Check billable/non-billable classification
4. **Export both CSV and JSON** - CSV for accounting, JSON for records

### Calendar Sync

1. **Start with one-way sync** (to calendar) to test
2. **Enable two-way sync** after confirming it works
3. **Set up webhooks** for real-time updates
4. **Sync regularly** - Daily or weekly for best results
5. **Use calendar colors** to distinguish Focus tasks from regular events

### Offline Mode

1. **Install PWA** for best offline experience
2. **Sync before going offline** to have latest data
3. **Queue operations** instead of failing when offline
4. **Monitor sync queue** - Check pending count in UI
5. **Clear queue manually** if sync fails repeatedly

---

## Troubleshooting

### Invoice Generation Issues

**Problem:** "No billable hours found"
- **Solution:** Ensure time entries are marked as billable
- Check date range includes time entries

**Problem:** Invoice shows $0 amount
- **Solution:** Set hourly_rate in time entries or override in request

### Calendar Sync Issues

**Problem:** OAuth fails
- **Solution:** Check Google OAuth credentials in .env
- Ensure redirect_uri matches Google Console

**Problem:** Tasks not appearing in calendar
- **Solution:** Verify tasks have due dates
- Check sync direction is "to_calendar" or "both"

**Problem:** Duplicate events
- **Solution:** Run sync less frequently
- Check for conflicting sync setups (e.g., multiple apps syncing)

### Offline Mode Issues

**Problem:** Data not syncing when online
- **Solution:** Check service worker is registered
- Manually trigger sync: `navigator.serviceWorker.ready.then(r => r.sync.register('sync-offline-data'))`

**Problem:** IndexedDB quota exceeded
- **Solution:** Clear old data periodically
- Reduce number of offline items stored

---

## Future Enhancements

### Planned Features

1. **PDF Invoice Generation** - Professional PDF invoices with branding
2. **Multiple Calendar Support** - Sync with work, personal calendars separately
3. **Zapier Integration** - Connect to 1000+ apps
4. **Slack Integration** - Create tasks from Slack messages
5. **Native Mobile Apps** - iOS and Android native apps

### Experimental Features

1. **Voice-based time tracking** - Start/stop timers via voice
2. **AI-powered invoice categorization** - Auto-tag billable hours
3. **Smart calendar suggestions** - AI suggests optimal task scheduling
4. **Offline AI** - Run lightweight AI models locally in PWA

---

## Support & Resources

### Documentation
- API Docs: http://localhost:8000/docs
- User Guide (archived): /_archive/docs/USER_GUIDE.md
- Developer Guide (archived): /_archive/docs/DEVELOPER_GUIDE.md

### Source Code
- Backend: /backend/app/routers/exports.py
- Backend: /backend/app/routers/calendar_sync.py
- Frontend: /frontend/src/lib/utils/offlineStorage.ts
- Service Worker: /frontend/static/service-worker.js
- II-Agent Tools: /ii-agent/src/ii_agent/tools/focus_tools.py

### Community
- GitHub Issues: Report bugs and feature requests
- Discussions: Ask questions and share tips
- Slack Channel: Real-time support and community

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Maintained By:** Focus by Kraliki Team
