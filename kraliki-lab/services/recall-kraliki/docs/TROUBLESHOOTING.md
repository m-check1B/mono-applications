# Troubleshooting Recall by Kraliki

Common issues and solutions.

## Backend Issues

### Backend Won't Start

**Error:** `Address already in use (port 3020)`

**Solution:**
```bash
# Find and kill process using port 3020
lsof -i :3020
kill -9 [PID]

# Or kill all uvicorn processes
pkill -f uvicorn

# Then restart
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 3020
```

---

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Activate virtual environment
cd backend
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

**Error:** `No module named 'zhipuai'`

**Solution:**
```bash
# Install GLM 4.6 API client
source .venv/bin/activate
pip install zhipuai>=2.0.0
```

---

### API Returns Errors

**Error:** `500 Internal Server Error`

**Check logs:**
```bash
# If running in background
tail -f /tmp/recall-backend.log

# If running in foreground, check terminal output
```

**Common causes:**
1. `.env` file missing → Copy `.env.example` to `.env`
2. `ZHIPUAI_API_KEY` not set → Add key to `.env`
3. `memory/` folder missing → Create: `mkdir -p memory/{decisions,insights,ideas,learnings,customers,competitors,research,sessions}`

---

**Error:** `"detail": "Search failed: 'file_path'"`

**Solution:**
This is a field name inconsistency bug. Fixed in latest version. Update `app/services/storage.py`:

```bash
cd backend
sed -i 's/"filepath":/"file_path":/g' app/services/storage.py
```

Then restart backend.

---

## Frontend Issues

### Frontend Won't Start

**Error:** `Port 5176 is already in use`

**Solution:**
```bash
# Kill process using port 5176
lsof -i :5176
kill -9 [PID]

# Or use different port
pnpm dev --port 5177
```

---

**Error:** `Cannot find module '@sveltejs/kit'`

**Solution:**
```bash
cd frontend
pnpm install
```

---

**Error:** `The `prose` class does not exist`

**Solution:**
This is a Tailwind Typography issue. Fixed in latest version. The `prose` class was removed from `app.css`.

If you see this error:
```bash
cd frontend/src
# Remove prose classes from app.css
sed -i 's/@apply prose prose-sm max-w-none;//g' app.css
```

Then restart frontend.

---

### Frontend Loads But Looks Wrong

**Issue:** No dark mode styles

**Solution:**
```bash
# Check Tailwind config has darkMode
cd frontend
grep "darkMode" tailwind.config.js

# Should see:
# darkMode: 'class',
```

If missing, add to `tailwind.config.js`:
```javascript
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',  // <-- Add this
  theme: { extend: {} }
}
```

---

**Issue:** Styles not updating

**Solution:**
```bash
# Clear Vite cache
cd frontend
rm -rf .svelte-kit
rm -rf node_modules/.vite
pnpm dev
```

---

## Search Issues

### Search Returns No Results

**Check 1:** Verify items exist
```bash
ls memory/decisions/
ls memory/insights/
# Should see .md files
```

**Check 2:** Verify backend is running
```bash
curl http://127.0.0.1:3020/health
# Should return: {"status":"healthy",...}
```

**Check 3:** Test API directly
```bash
curl http://127.0.0.1:3020/api/capture/recent?limit=10
# Should return JSON with items
```

**Check 4:** Check search endpoint
```bash
curl -X POST http://127.0.0.1:3020/api/search/ \
  -H "Content-Type: application/json" \
  -d '{"query":"test","search_type":"keyword"}'
```

---

### Semantic Search Not Working

**Issue:** Semantic search returns same results as keyword

**Cause:** GLM 4.6 API not configured or not responding

**Solution:**

1. Check `.env` file:
```bash
cat backend/.env | grep ZHIPUAI_API_KEY
# Should show your API key
```

2. Test GLM API:
```bash
cd backend
source .venv/bin/activate
python -c "from zhipuai import ZhipuAI; import os; from dotenv import load_dotenv; load_dotenv(); client = ZhipuAI(api_key=os.getenv('ZHIPUAI_API_KEY')); print('GLM 4.6 API connected!' if client else 'Failed')"
```

3. Check API quota/limits in ZhipuAI dashboard

---

## Capture Issues

### Can't Capture Items

**Error:** `Failed to capture item`

**Check 1:** Backend running?
```bash
curl http://127.0.0.1:3020/health
```

**Check 2:** Memory directories exist?
```bash
ls memory/
# Should see: decisions/ insights/ ideas/ etc.
```

If missing:
```bash
mkdir -p memory/{decisions,insights,ideas,learnings,customers,competitors,research,sessions}
```

**Check 3:** Permissions?
```bash
# Check if you can write to memory/
touch memory/test.txt
rm memory/test.txt
```

---

### Auto-Categorize Not Working

**Issue:** Items always go to same category or fail

**Cause:** GLM 4.6 API issue

**Solution:**
1. Disable auto-categorize temporarily
2. Manually select category
3. Check GLM API status (see Semantic Search section above)

---

## Graph Issues

### Graph Shows No Nodes

**Issue:** Graph page shows 0 nodes

**Cause:** No items captured yet OR API issue

**Solution:**

1. Capture at least 1 item first
2. Check API:
```bash
curl http://127.0.0.1:3020/api/graph/
# Should return JSON with nodes array
```

3. Check browser console (F12) for errors

---

### Graph Shows Nodes But No Connections

**Issue:** Nodes visible but edges = 0

**Cause:** No wikilinks or related items

**Solution:**
Wikilinks/relationships are created when:
- You use `[[category/id|label]]` syntax
- Auto-link finds related items
- Items share tags

Add wikilinks to items:
```markdown
Related:
- [[decisions/dec-2025-10-06-001|Previous decision]]
```

---

## Dark Mode Issues

### Dark Mode Not Persisting

**Issue:** Dark mode resets after refresh

**Cause:** localStorage not working OR theme store issue

**Solution:**

1. Check browser console (F12) for errors
2. Test localStorage:
```javascript
// In browser console
localStorage.setItem('test', 'value')
localStorage.getItem('test')  // Should return 'value'
```

3. Check theme store exists:
```bash
ls frontend/src/lib/stores/theme.ts
```

4. Clear browser cache and try again

---

### Dark Mode Toggle Not Visible

**Issue:** Can't see 🌙 button

**Cause:** Layout component not updated

**Solution:**
```bash
cd frontend/src/routes
grep "toggleTheme" +layout.svelte
# Should see theme toggle button code
```

If missing, update `+layout.svelte` to include dark mode toggle.

---

## Performance Issues

### Frontend Slow to Load

**Solution:**

1. Build for production:
```bash
cd frontend
pnpm build
pnpm preview
```

2. Check network tab (F12) for slow requests

3. Reduce memory directory size if > 1000 files

---

### Search Takes Too Long

**Solution:**

1. Use keyword search instead of hybrid/semantic for large datasets

2. Limit results:
```javascript
// In search request
{ query: "test", limit: 10 }
```

3. Index memory directory:
```bash
# Rebuild search index (if implemented)
cd backend
python scripts/rebuild_index.py
```

---

## Data Issues

### Lost Data After Restart

**Cause:** Memory files deleted OR wrong directory

**Solution:**

1. Check memory folder exists:
```bash
ls memory/
```

2. Check git history:
```bash
git log -- memory/
git checkout HEAD~1 -- memory/  # Restore from previous commit
```

3. Check backups:
```bash
ls ~/recall-backups/
```

---

### Duplicate Items

**Issue:** Same item appears multiple times

**Cause:** ID generation collision

**Solution:**

```bash
# Find duplicates
cd memory/decisions
ls -l | grep "dec-2025-10-07-001"

# If found, manually rename one:
mv dec-2025-10-07-001-untitled.md dec-2025-10-07-002-untitled.md
# Update ID in YAML frontmatter
```

---

## MCP Server Issues

### Claude Code Can't Find MCP Server

**Solution:**

1. Check MCP server path in Claude Code settings:
```json
{
  "mcpServers": {
    "recall-kraliki": {
      "command": "python",
      "args": ["/home/adminmatej/github/applications/kraliki-lab/services/recall-kraliki/mcp-server/server.py"],
      "envFile": "/home/adminmatej/github/applications/kraliki-lab/services/recall-kraliki/.env"
    }
  }
}
```

2. Verify server.py exists:
```bash
ls /home/adminmatej/github/applications/kraliki-lab/services/recall-kraliki/mcp-server/server.py
```

3. Test MCP server manually:
```bash
cd mcp-server
python server.py
# Should start without errors
```

---

## Getting More Help

1. **Check logs:**
   - Backend: Terminal where uvicorn is running
   - Frontend: Browser console (F12)
   - MCP: Claude Code logs

2. **Enable debug mode:**
   ```bash
   # Backend
   DEBUG=True uvicorn app.main:app --reload

   # Frontend
   pnpm dev --debug
   ```

3. **GitHub Issues:**
   https://github.com/m-check1B/recall-kraliki/issues

4. **Documentation:**
   - `README.md` - Overview
   - `docs/GETTING-STARTED.md` - Quick start
   - `docs/USER-GUIDE.md` - Full guide
   - `docs/CLAUDE.md` - Technical docs

---

**Still stuck?** Create an issue on GitHub with:
- Error message (exact text)
- Steps to reproduce
- System info (`uname -a`, Python version, Node version)
- Logs (backend and frontend)
