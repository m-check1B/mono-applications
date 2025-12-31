# Mac Computer Use Cookbook: Soldier Portal

**App:** soldier-portal
**Description:** Mission Control for Ocelot Field Operatives
**Created:** 2025-12-23
**Linear:** VD-167

---

## Purpose

This cookbook enables Mac Computer Use (Claude Desktop) to perform visual and manual testing of the Soldier Portal. The portal is a lightweight web app for contractors to execute queue tasks without touching code or file systems.

---

## Access Information

### Current Status

- App repo location: `TBD` (expected: `/github/applications/soldier-portal/`)
- Spec reference: `/github/verduona-business/specs/SOLDIER-PORTAL-MVP.md`
- Login provider: Zitadel (OIDC)
- Deployment: Not yet live

### When Dev Server Exists

```bash
# Example commands once repo exists
cd /github/applications/soldier-portal
npm install
npm run dev

# Access on the Mac
http://127.0.0.1:3000
```

---

## Visual Elements to Verify

### 1. Login Screen

```
VERIFY:
[ ] Centered card with "Ocelot Soldier Portal"
[ ] Single primary button: "Sign in with Ocelot ID"
[ ] No extra links or clutter
```

### 2. Dashboard (Home)

```
VERIFY:
[ ] Welcome message includes user name
[ ] Queue cards show category + pending count
[ ] Cards are large, touch-friendly, and evenly spaced
[ ] Only relevant queues visible for the role
```

### 3. Queue List View

```
VERIFY:
[ ] List items show human-readable task names
[ ] Modified timestamps visible
[ ] "Ready" status badge is green
[ ] Clicking opens task view
```

### 4. Task Execution View

```
VERIFY:
[ ] Markdown content renders cleanly
[ ] Copy to Clipboard button present
[ ] "Mark as Complete" is primary CTA
[ ] "Report Issue" is secondary CTA
```

### 5. Mobile Layout

```
VERIFY:
[ ] No horizontal scroll on iPhone size
[ ] Buttons remain thumb-sized
[ ] Cards stack vertically
```

---

## Payment Flows

### Current Status: Not Applicable

The Soldier Portal has no payment flows in the MVP.

---

## OAuth/Identity Setup

### Zitadel OIDC

```
VERIFY:
[ ] Login redirects to identity provider
[ ] Session persists on reload
[ ] Role-based access: admin vs soldier
```

If credentials are missing, request test accounts from `/github/secrets/test-accounts/` or open a HW task.

---

## Expected States (Screenshots)

### Dashboard Example

```
Welcome, Alex. Ready to work?

[ Email Dispatch ] [3 Pending]
[ Contract Signing ] [1 Pending]
[ Content Publish ] [5 Pending]
[ Call Prep ] [0 Pending]
```

### Task View Example

```
Task: Prospect Outreach Email

To: jan@company.cz
Subject: AI Workshop Invitation
Body: ...

[ Copy to Clipboard ]
[ Mark as Complete ]  [ Report Issue ]
```

---

## Testing Checklist

### Pre-Testing

- [ ] Dev server running on 127.0.0.1
- [ ] Login credentials available
- [ ] Sample queue files exist

### Core Functionality

- [ ] Login works and redirects to dashboard
- [ ] Queue cards show correct counts
- [ ] Task view renders Markdown accurately
- [ ] Copy to Clipboard works
- [ ] Mark as Complete moves file and logs action

### Mobile

- [ ] Dashboard usable on phone
- [ ] Task view readable without zoom

---

## Reporting Issues

If tests fail, create a human-work note:

```bash
cd /github/ai-automation/humans-work-needed
# Create issue: HW-XXX_soldier-portal-issue.md
```

Then update `features.json` with the new HW blocker.

---

## Quick Reference

```bash
# Spec doc
cat /github/verduona-business/specs/SOLDIER-PORTAL-MVP.md

# Once repo exists
cd /github/applications/soldier-portal
npm run dev
```

---

*Cookbook Version: 1.0*
*Created: 2025-12-23*
*For: Mac Claude Desktop Computer Use*
*Linear Task: VD-167*
