# Gemini File Search Integration - Documentation

## Overview

The Gemini File Search integration adds **semantic search capabilities** to Focus by Kraliki, allowing users to search their knowledge base using natural language queries. The system uses Google's Gemini API with File Search to provide AI-generated answers grounded in the user's actual content.

**Status:** ✅ Production-ready (as of November 14, 2025)

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Setup & Configuration](#setup--configuration)
4. [How It Works](#how-it-works)
5. [API Reference](#api-reference)
6. [Frontend Usage](#frontend-usage)
7. [II-Agent Integration](#ii-agent-integration)
8. [Troubleshooting](#troubleshooting)
9. [Performance & Scaling](#performance--scaling)
10. [Security & Privacy](#security--privacy)

---

## Features

### Core Capabilities

✅ **Semantic Search** - Natural language queries over knowledge base
✅ **AI-Generated Answers** - Grounded responses with source citations
✅ **Auto-Import** - Knowledge items automatically indexed
✅ **Voice Transcripts** - Voice recordings searchable after processing
✅ **II-Agent Tool** - Agent can recall past conversations and decisions
✅ **Graceful Fallback** - SQL-based search when Gemini unavailable
✅ **Organization-Scoped** - Multi-tenant security built-in

### Example Queries

- "What did I decide about the database migration?"
- "Find my notes about the project architecture"
- "What are my priorities this week?"
- "What tasks did I create related to the API redesign?"
- "Summarize my meetings from last week"

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│              (Knowledge Hub + AI Search Panel)               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST /ai/file-search/query
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Focus by Kraliki Backend (FastAPI)                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  AI File Search Router                             │    │
│  │  • POST /ai/file-search/query                      │    │
│  │  • GET  /ai/file-search/status                     │    │
│  │  • POST /ai/file-search/import                     │    │
│  │  • GET  /ai/file-search/documents                  │    │
│  └────────────────────┬───────────────────────────────┘    │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────┐    │
│  │  Gemini File Search Service                        │    │
│  │  • get_or_create_org_store()                       │    │
│  │  • import_knowledge_item()                         │    │
│  │  • query_store()                                   │    │
│  │  • _sql_fallback_search()                          │    │
│  └────────────────────┬───────────────────────────────┘    │
│                       │                                      │
└───────────────────────┼──────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────────┐       ┌──────────────────────┐
│  Google Gemini    │       │  PostgreSQL          │
│  File Search API  │       │  • file_search_store │
│                   │       │  • file_search_doc   │
│  • Store Creation │       │  • knowledge_item    │
│  • Document Upload│       └──────────────────────┘
│  • Semantic Query │
└───────────────────┘
```

### Data Flow

1. **Knowledge Item Created** → Background task → Auto-import to File Search
2. **User Queries** → Backend → Gemini File Search → AI Answer + Citations
3. **Citations** → Mapped to knowledge items → Frontend displays sources
4. **Gemini Unavailable** → Fallback to SQL ILIKE search

---

## Setup & Configuration

### Prerequisites

- PostgreSQL database (already configured)
- Python 3.14+ with FastAPI backend
- Google Cloud account with Gemini API access (optional)

### 1. Database Migrations

Run the migrations to create File Search tables:

```bash
cd /home/adminmatej/github/applications/focus-kraliki/backend
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade 008 -> efc5b5c84ee7, add_file_search_store_table
INFO  [alembic.runtime.migration] Running upgrade efc5b5c84ee7 -> 1b7ebd476b75, add_file_search_documents_mapping_table
```

### 2. Environment Variables

Edit `backend/.env` (or set environment variables):

```env
# Required for full functionality (optional - works without)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - defaults shown
GEMINI_FILE_SEARCH_PROJECT_ID=         # Google Cloud project ID (if needed)
GEMINI_FILE_SEARCH_LOCATION=us-central1  # Gemini service location
```

**To obtain a Gemini API key:**
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create or select a project
3. Generate an API key
4. Copy key to `.env` file

### 3. Install Dependencies (Optional)

If using Gemini File Search:

```bash
pip install google-generativeai
```

**Note:** The system works without this dependency by using SQL fallback.

### 4. Restart Services

```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# No changes needed for frontend or II-Agent
```

### 5. Verify Installation

**Check backend health:**
```bash
curl http://localhost:8000/ai/file-search/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "gemini_available": true,  // or false if API key not configured
  "gemini_configured": true,
  "api_key_present": true
}
```

---

## How It Works

### Auto-Import on Knowledge Item Creation

When a user creates or updates a knowledge item, Focus by Kraliki automatically imports it to Gemini File Search in the background:

```python
# In knowledge.py router
@router.post("/knowledge/items")
async def create_knowledge_item(..., background_tasks: BackgroundTasks):
    # Create item in database
    knowledge_item = ...

    # Schedule background import (non-blocking)
    background_tasks.add_task(
        import_knowledge_item_background,
        db=db,
        user=current_user,
        item=knowledge_item
    )

    # Return immediately (< 50ms)
    return knowledge_item
```

**What gets imported:**
- Title + Content (combined into document)
- Metadata: organization_id, user_id, knowledge_item_id, type_id, completed status
- Timestamps: created_at, updated_at

### Semantic Query Process

1. **User submits query** via AI Search Panel or II-Agent
2. **Backend retrieves** organization's File Search store (or creates if needed)
3. **Gemini processes** query with File Search tool:
   - Performs semantic search over indexed documents
   - Generates AI answer grounded in user's content
   - Returns citations with excerpts
4. **Backend maps citations** to knowledge items using metadata
5. **Frontend displays** answer + clickable source links

### Fallback Mechanism

If Gemini is unavailable or not configured:

```python
# Automatic fallback in query_store()
except Exception as e:
    logger.error(f"Failed to query File Search: {e}")
    # Fallback to SQL search
    return await _sql_fallback_search(db, user, prompt)
```

**SQL Fallback Search:**
- Uses PostgreSQL ILIKE for text search
- Searches knowledge item titles and content
- Returns top 5 results with excerpts
- Same response format as Gemini

---

## API Reference

### POST /ai/file-search/query

Search the knowledge base using natural language.

**Request:**
```json
{
  "query": "What are my priorities this week?",
  "context": {  // optional
    "type_id": "abc123",  // Filter by item type
    "project_id": "xyz789"  // Filter by project
  }
}
```

**Response:**
```json
{
  "answer": "Based on your notes, your priorities this week are: 1) Complete the API integration...",
  "citations": [
    {
      "documentName": "Weekly Planning - Nov 14.txt",
      "knowledgeItemId": "item-123",
      "excerpt": "This week I need to focus on..."
    }
  ],
  "model": "gemini-2.0-flash-exp",
  "store_name": "fileSearchStores/abc123xyz",
  "fallback_used": false
}
```

**Status Codes:**
- `200 OK` - Query successful (even if using fallback)
- `401 Unauthorized` - Invalid or missing JWT token
- `422 Unprocessable Entity` - Invalid request format
- `500 Internal Server Error` - Unexpected server error

---

### GET /ai/file-search/status

Check File Search service status.

**Request:**
```bash
curl http://localhost:8000/ai/file-search/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "gemini_available": true,
  "gemini_configured": true,
  "store_exists": true,
  "store_name": "fileSearchStores/abc123xyz",
  "document_count": 42,
  "organization_id": "org-123"
}
```

---

### POST /ai/file-search/import

Manually import a knowledge item.

**Request:**
```json
{
  "knowledge_item_id": "item-123"
}
```

**Response:**
```json
{
  "success": true,
  "document_name": "files/doc-456.txt",
  "store_name": "fileSearchStores/abc123xyz"
}
```

---

### GET /ai/file-search/documents

List all documents in the File Search store.

**Request:**
```bash
curl http://localhost:8000/ai/file-search/documents \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "store_name": "fileSearchStores/abc123xyz",
  "documents": [
    {
      "name": "files/doc-123.txt",
      "display_name": "My Project Notes",
      "size_bytes": 1024,
      "create_time": "2025-11-14T10:30:00Z"
    }
  ],
  "total_count": 1
}
```

---

### GET /ai/file-search/health

Quick health check (no authentication required).

**Request:**
```bash
curl http://localhost:8000/ai/file-search/health
```

**Response:**
```json
{
  "status": "healthy",
  "gemini_available": true,
  "gemini_configured": true,
  "api_key_present": true
}
```

---

## Frontend Usage

### AI Search Panel Component

Located at: `frontend/src/lib/components/knowledge/AISearchPanel.svelte`

**Usage in Knowledge Hub:**

```svelte
<script>
  import AISearchPanel from '$lib/components/knowledge/AISearchPanel.svelte';
</script>

<div class="knowledge-hub">
  <!-- AI Search Panel -->
  <AISearchPanel />

  <!-- Rest of page... -->
</div>
```

**User Experience:**

1. User types natural language query in search box
2. Click "Search" button or press Enter
3. Loading state shows "Searching..."
4. Results display:
   - AI-generated answer (Markdown formatted)
   - List of sources (numbered citations)
   - Click citation → highlights knowledge item in grid
5. Error states show helpful messages

**Example Queries:**

Good queries:
- "What did I decide about X?"
- "Find notes about Y"
- "What are my Z priorities?"

Poor queries (too vague):
- "stuff"
- "things"
- "help"

---

## II-Agent Integration

### Focus File Search Tool

Located at: `ii-agent/src/ii_agent/tools/focus_tools.py`

**Tool Name:** `focus_file_search_query`

**When Agent Uses It:**

- User asks about past decisions or notes
- Agent needs context for complex workflows
- User requests information recall

**Example Workflow:**

```
User: "What did I decide about the database migration?"

Agent (internal):
  → Calls focus_file_search_query
  → Query: "database migration decisions"
  → Receives: "You decided to use PostgreSQL with Alembic..."

Agent (to user):
  "Based on your notes from last week, you decided to use PostgreSQL
   with Alembic for migrations because it provides better version control
   and rollback capabilities."
```

**Tool Registration:**

The tool is automatically available when Focus tools are enabled:

```typescript
const toolArgs = {
  focus_tools: true,
  focus_api_base_url: "http://127.0.0.1:8000",
  agent_token: agentToken  // Required for authentication
};
```

**Tool Output Format:**

```
**Answer:** [AI-generated answer based on user's content]

**Sources:**
1. Weekly Planning - Nov 14.txt (ID: item-123)
   Excerpt: "This week I need to focus on..."
2. Database Migration Notes (ID: item-456)
   Excerpt: "After research, decided on PostgreSQL..."
```

---

## Troubleshooting

### Issue: "Gemini File Search not working"

**Check 1: API Key Configuration**
```bash
# In backend container/shell
python -c "from app.core.config import settings; print(settings.GEMINI_API_KEY)"
```

Expected: Your API key (starts with `AI...`)
If `None` → Set `GEMINI_API_KEY` in `.env`

**Check 2: Dependencies**
```bash
pip list | grep generativeai
```

Expected: `google-generativeai  0.x.x`
If missing → `pip install google-generativeai`

**Check 3: Service Health**
```bash
curl http://localhost:8000/ai/file-search/health
```

Expected: `{"status": "healthy", "gemini_available": true}`

---

### Issue: "No results found"

**Possible Causes:**

1. **No documents indexed yet**
   - Create some knowledge items first
   - Wait 2-3 seconds for background import
   - Check logs: `grep "File Search import" backend.log`

2. **Query too vague**
   - Be more specific in query
   - Use keywords from your actual content

3. **Gemini unavailable → SQL fallback**
   - Check response for `"fallback_used": true`
   - SQL search is less powerful than semantic search

---

### Issue: "Citations not linking to items"

**Check:**
- Citation should have `knowledgeItemId` field
- Item should still exist in database
- User should have access to that item (same organization)

**Fix:**
- Re-import the knowledge item:
  ```bash
  curl -X POST http://localhost:8000/ai/file-search/import \
    -H "Authorization: Bearer TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"knowledge_item_id": "item-123"}'
  ```

---

### Issue: "Slow responses"

**Expected Response Times:**
- SQL fallback: < 100ms
- Gemini File Search: 1-3 seconds (normal)
- Background import: 1-2 seconds (non-blocking)

**If slower than expected:**
1. Check Gemini API status: https://status.cloud.google.com/
2. Check network latency to Gemini servers
3. Consider reducing document size or count

---

## Performance & Scaling

### Current Limits

| Metric | Limit | Notes |
|--------|-------|-------|
| Documents per store | ~10,000 | Gemini recommendation |
| Store size | ~20GB | Keep below for best performance |
| Query latency (p95) | < 3s | With Gemini File Search |
| Import latency | 1-2s | Background task (non-blocking) |
| Concurrent queries | No limit | Limited by backend workers |

### Optimization Tips

**For Large Knowledge Bases (1000+ items):**

1. **Use specific queries** - More specific = faster results
2. **Filter by type** - Use `context.type_id` to narrow search
3. **Archive old items** - Move outdated content to separate type
4. **Batch imports** - Create items in bulk, let background tasks handle import

**For High Query Volume:**

1. **Cache results** - Consider Redis for frequently asked queries
2. **Rate limiting** - Protect against abuse (not implemented yet)
3. **Monitor quotas** - Track Gemini API usage

### Cost Considerations

**Gemini API Pricing (as of Nov 2025):**
- File Search queries: ~$0.0015 per query (1K tokens)
- Document storage: Included in API pricing
- Estimated cost: $0.01-0.05 per user per month (typical usage)

**To reduce costs:**
- Use SQL fallback for simple queries
- Implement query caching
- Set up usage alerts in Google Cloud

---

## Security & Privacy

### Data Security

✅ **Organization-Scoped Stores** - Each organization has isolated File Search store
✅ **User Authentication** - All endpoints require valid JWT token
✅ **Metadata Filtering** - Queries automatically filtered by organization ID
✅ **Cascade Deletes** - Removing user/org removes associated File Search data

### Privacy Considerations

⚠️ **Data Sent to Google Gemini:**
- Knowledge item content (title + text)
- User IDs and organization IDs (as metadata)
- Voice transcript text

⚠️ **Not Sent to Google:**
- User passwords or credentials
- JWT tokens
- Database records (only indexed content)

### Compliance

**Before Production:**

1. **Review Data Policy** - Ensure sending data to Gemini complies with your policies
2. **Update Privacy Policy** - Inform users that AI search uses Google Gemini
3. **Consider Opt-In** - Allow users/organizations to enable/disable feature
4. **Data Retention** - Document how long data stays in Gemini File Search
5. **GDPR/CCPA** - Ensure compliance with data regulations

**Recommended Approach:**

Add to user settings:
```
☐ Enable AI-powered semantic search (uses Google Gemini)
   Your knowledge will be processed by Google's AI to provide better search results.
   [Learn more about data privacy]
```

---

## Maintenance

### Monitoring

**Key Metrics to Track:**

1. **Gemini API Usage**
   - Queries per day
   - Cost per month
   - Error rate

2. **Fallback Frequency**
   - How often SQL fallback is used
   - Indicates Gemini availability

3. **Import Success Rate**
   - Background task failures
   - Items not imported

4. **Store Sizes**
   - Track document count per organization
   - Alert if approaching 10,000 documents

### Logs to Monitor

```bash
# Backend logs
tail -f backend.log | grep "File Search"

# Look for:
# - "Successfully imported knowledge item"
# - "Failed to import knowledge item"
# - "Gemini unavailable - using SQL fallback"
# - "File Search query completed"
```

### Cleanup Tasks

**Periodic Maintenance:**

1. **Archive Old Stores** - Remove abandoned organizations
2. **Delete Orphaned Documents** - Clean up documents without knowledge items
3. **Optimize Indexes** - Rebuild database indexes if slow

---

## FAQ

### Q: Can I use this without a Gemini API key?

**A:** Yes! The system falls back to SQL-based text search automatically. You'll still get results, but they won't be as intelligent as semantic search.

### Q: How do I know if File Search is working?

**A:** Check `/ai/file-search/health` endpoint or look for `"fallback_used": false` in query responses.

### Q: Can users opt out of File Search?

**A:** Not currently implemented. Consider adding an organization-level setting to disable auto-import.

### Q: What happens if I delete a knowledge item?

**A:** The document remains in File Search (for now). Future enhancement: auto-delete from File Search on item deletion.

### Q: How do I bulk import existing knowledge items?

**A:** Use the `/ai/file-search/import` endpoint in a loop, or implement a bulk import script.

### Q: Is voice transcript search automatic?

**A:** Yes! If voice transcription is enabled, transcripts are auto-imported after processing.

### Q: Can I search across multiple organizations?

**A:** No. File Search stores are organization-scoped for security. Each org has isolated data.

### Q: What's the difference between File Search and the existing AI chat?

**A:** AI chat is for simple function-calling (create/update tasks). File Search is for semantic knowledge retrieval over historical data.

---

## Advanced Usage

### Custom Metadata Filtering

When querying, you can pass context to filter results:

```json
{
  "query": "What are my priorities?",
  "context": {
    "type_id": "idea-type-123",  // Only search ideas
    "completed": false,           // Only incomplete items
    "project_id": "proj-456"      // Only specific project
  }
}
```

### Programmatic Access

Use the API client in your own code:

```typescript
import { aiFileSearchQuery } from '$lib/api/ai_file_search';

const result = await aiFileSearchQuery(
  "What did I decide about X?",
  { project_id: "abc123" }
);

console.log(result.answer);
result.citations.forEach(c => console.log(c.knowledgeItemId));
```

---

## Support

**Issues & Questions:**
- Check logs: `backend/logs/` and browser console
- Review troubleshooting section above
- Check Gemini API status: https://status.cloud.google.com/

**Contributing:**
- File bugs in project issue tracker
- Submit PRs for improvements
- Update this documentation as features evolve

---

## Changelog

### v1.0.0 (2025-11-14)
- ✅ Initial implementation
- ✅ Backend API endpoints (5 total)
- ✅ Frontend AI Search Panel
- ✅ II-Agent tool integration
- ✅ Auto-import on create/update
- ✅ Voice transcript support
- ✅ SQL fallback mechanism
- ✅ Comprehensive error handling

### Future Enhancements
- ⏳ Opt-in/opt-out per organization
- ⏳ Rate limiting
- ⏳ Query caching
- ⏳ Document pruning mechanism
- ⏳ Bulk import utility
- ⏳ Auto-delete on knowledge item deletion
- ⏳ Advanced filtering UI
- ⏳ Search history

---

**Last Updated:** November 14, 2025
**Version:** 1.0.0
**Maintained By:** Focus by Kraliki Development Team
