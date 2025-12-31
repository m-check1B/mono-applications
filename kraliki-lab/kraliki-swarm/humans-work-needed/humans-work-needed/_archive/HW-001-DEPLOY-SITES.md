# Human Task: Deploy Marketing Sites (Launch Day 1)

**Priority:** HIGH
**Due:** 2025-12-22
**Context:** We are starting the "Brace the Impact" launch sequence.

## Actions Required

1.  **Stage Sites:**
    Run the helper script to prepare the build:
    ```bash
    cd /home/adminmatej/github/marketing-2026
    ./scripts/prepare_dist.sh
    ```

2.  **Deploy Sites:**
    Copy the staged folder to your websites repo and push/deploy:
    ```bash
    cp -r dist/* ../websites/
    # Then commit and push in ../websites/ if that triggers your deployment pipeline
    ```

3.  **Confirm:**
    Check that `tldr.verduona.localhost` (or the production URL) displays the new "Telegram Stars" pricing.

## Status Update
Once done, please delete this file or move to `ai-automation/humans-work-needed/archive/`.
