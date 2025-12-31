# Action Required: Regenerate Linear API Key

**Priority:** HIGH
**Due:** As soon as possible
**Context:** Linear API key has expired. Darwin2 dashboard and Linear sync are not working.

## Problem

The Linear API key at `/github/secrets/linear_api_key.txt` is returning 401 Authentication errors.
This blocks:
- Darwin2 Linear sync service
- Dashboard Linear task display
- Agent task assignment from Linear

## Required Actions

1. **Generate new Linear API key:**
   - Go to https://linear.app/settings/api
   - Create a new Personal API Key (or regenerate existing)
   - Copy the new key

2. **Update secrets file:**
   ```bash
   echo "NEW_API_KEY_HERE" > /github/secrets/linear_api_key.txt
   ```

3. **Restart Linear sync service:**
   ```bash
   pm2 restart darwin2-linear-sync
   ```

4. **Verify:**
   ```bash
   curl -s -X POST https://api.linear.app/graphql \
     -H "Authorization: $(cat /github/secrets/linear_api_key.txt)" \
     -H "Content-Type: application/json" \
     -d '{"query": "query { viewer { id name } }"}'
   ```

5. **Confirm:**
   - Move this file to `done/` folder when complete.

## Impact

Darwin2 agents cannot receive new tasks from Linear until this is fixed.
Linear dashboard data is stale.
