# HW-022: Deploy Sites

**Status:** BLOCKED (Needs Human)
**Context:** Launch Checklist Day 1
**Goal:** Push staged landing pages to production repo/server.

## Instructions
1.  Go to the marketing repo:
    ```bash
    cd /home/adminmatej/github/marketing-2026/
    ```
2.  Verify the staged build:
    ```bash
    # (Already ran ./scripts/prepare_dist.sh)
    ls dist/
    ```
3.  Copy to websites repo (or deployment target):
    ```bash
    cp -r dist/* ../websites/
    # OR if deploying to a specific server folder:
    # rsync -avz dist/ user@5.9.38.218:/var/www/verduona/
    ```
4.  Commit and Push (if using GitOps):
    ```bash
    cd ../websites/
    git add .
    git commit -m "Deploy launch sites - Jan 2026 Campaign"
    git push
    ```
5.  **Verify DNS:** Ensure `HW-006` / `HW-017` (DNS setup) is complete so these sites are accessible.

## Definition of Done
- [ ] `verduona.com` shows "Brace the AI Impact".
- [ ] `business.verduona.com` shows Workshop landing.
- [ ] `tldr.verduona.com` shows TL;DR bot landing.
