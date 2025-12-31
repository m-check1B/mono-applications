# HW-003: Production Server Status Check

**Status:** OBSOLETE (2025-12-20) - Using dev server for websites
**Blocks:** Website deployment to verduona.com
**Created:** 2025-12-09
**Priority:** HIGH

---

## Current Situation

- `verduona.com` DNS points to: `5.75.129.12`
- This dev server is: `5.9.38.218`
- When accessing https://verduona.com → Connection fails (000 response)

---

## What You Need To Do

1. SSH into the production server (5.75.129.12)
   ```bash
   ssh adminmatej@5.75.129.12
   ```
2. Check if server is running and what's deployed
3. Report back:
   - Is the server accessible?
   - What's currently running on it?
   - Is Caddy/nginx/Traefik installed?
   - What's the plan for this server?

**Alternative:** If production server isn't set up yet, consider:
- Deploy to Vercel/Netlify (free, instant SSL, no server management)
- Update DNS to point to this dev server (5.9.38.218) temporarily

---

## Expected Output

One of:
1. Server status and what's running
2. Decision: Use Vercel/Netlify instead
3. Decision: Point DNS to dev server temporarily

---

## When Done

1. Fill in the Result section below
2. Change Status above to: **DONE**

---

## Result

```
Server Status: [ACCESSIBLE / NOT ACCESSIBLE / DOES NOT EXIST]
What's running: [DESCRIBE]
Recommended action: [DESCRIBE]
```
