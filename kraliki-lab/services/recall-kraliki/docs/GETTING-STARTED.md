# Getting Started with Recall by Kraliki 🎯

**Never forget a decision, insight, or learning again.**

Recall by Kraliki is your persistent knowledge system that remembers everything across sessions using hybrid search (keyword + AI semantic search).

## Quick Start (5 minutes)

### 1. Start the System

**Terminal 1 - Backend:**
```bash
cd /home/adminmatej/github/applications/kraliki-lab/services/recall-kraliki/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 3020
```

**Terminal 2 - Frontend:**
```bash
cd /home/adminmatej/github/applications/kraliki-lab/services/recall-kraliki/frontend
pnpm dev --host 127.0.0.1 --port 5176
```

### 2. Open Recall by Kraliki

Open your browser to: **http://127.0.0.1:5176**

You'll see the search page with:
- 🔍 Search bar
- Category filter
- Search type selector (hybrid/keyword/semantic)
- 🌙 Dark mode toggle (top right)

### 3. Capture Your First Item

Click **"Capture"** in the navigation.

**Example 1 - Quick Decision:**
```markdown
# Decision: Use recall-kraliki for Ocelot Business

We're using recall-kraliki to capture all strategic decisions, insights, and learnings for the Ocelot business.

This solves the "AI amnesia" problem where Claude forgets everything between sessions.
```

- **Category**: Auto-categorize (AI will detect it's a "decision")
- **Tags**: `business, tools, knowledge-management`
- **Auto-categorize**: ✅ Checked
- **Auto-link**: ✅ Checked

Click **"Capture to recall-kraliki"**

✓ You'll see success message with:
- ID: `dec-2025-10-07-001`
- Category: `decisions`
- Tags: Auto-suggested by AI
- Related items: Auto-detected connections
- File path: Where it's saved

### 4. Search for It

Click **"Search"** → Type: `recall-kraliki`

You'll see your item appear with:
- Title
- Category badge
- Tags
- Content preview
- "View full item →" link

### 5. View Knowledge Graph

Click **"Graph"** to see:
- Nodes: Your captured items
- Connections: Wikilinks and related items
- Stats: Total nodes, edges, categories

## Daily Workflow

### Morning Routine

**Check Recent Items:**
```
Click "Recent" → See what you captured yesterday
```

**Search for Context:**
```
Search for project name or topic you're working on today
```

### During Work

**Capture Decisions:**
```markdown
# Decision: Use FastAPI for recall-kraliki backend

## Context
Need REST API for recall-kraliki. Options: Flask, Django, FastAPI.

## Decision
FastAPI - modern, fast, type-safe, async support.

## Related
- [[insights/ins-2025-10-06-001|Stack 2026 compliance]]
```

**Capture Insights:**
```markdown
# Insight: Hybrid search performs 24% better

Research shows hybrid search (keyword + semantic) achieves 81.67% accuracy vs 57.50% for pure vector search.

Source: mem-agent-mcp analysis
Tags: #ai #search #research
```

**Capture Ideas:**
```markdown
# Idea: Add voice notes to recall-kraliki

Let users speak decisions/insights via voice → auto-transcribe → auto-categorize.

Use case: Capture thoughts during commute or meetings.
```

**Capture Learnings:**
```markdown
# Learning: Dark mode needs all color variants

When adding dark mode to Svelte, must add dark: prefix to:
- Text colors (text-gray-700 → dark:text-gray-300)
- Backgrounds (bg-white → dark:bg-gray-800)
- Borders (border-gray-200 → dark:border-gray-700)

File: +layout.svelte, +page.svelte (all pages)
```

### End of Day

**Review the Day:**
```
Click "Recent" → Review what you captured
Click "Graph" → See how ideas connect
```

**Prepare for Tomorrow:**
```
Search for tomorrow's project → Get context loaded
```

## Using Wikilinks

**Syntax:**
```markdown
[[category/id|description]]
```

**Examples:**
```markdown
# Decision: Build recall-kraliki Phase 2 features

We'll add team collaboration based on [[insights/ins-2025-10-06-002|market research showing 73% demand]].

Related decisions:
- [[decisions/dec-2025-10-06-001|Initial recall-kraliki decision]]
- [[ideas/ide-2025-10-06-003|Multi-user architecture idea]]
```

When you view this item, wikilinks become clickable.

## Search Types

### Keyword Search (Fast, Exact)
```
Query: "FastAPI backend"
Returns: Items with exact words "FastAPI" and "backend"
Best for: Finding specific terms, file names, IDs
```

### Semantic Search (AI, Meaning)
```
Query: "backend framework choices"
Returns: Items about FastAPI, Flask, Django decisions
Best for: Finding related concepts, similar topics
```

### Hybrid Search (Recommended)
```
Query: "API design"
Returns: Keyword matches first, then semantic matches
Best for: Most queries - balances speed and intelligence
```

## Categories

**decisions** - Strategic choices and outcomes
```markdown
# Decision: Use GLM 4.6 instead of local LLM
```

**insights** - Key discoveries and learnings
```markdown
# Insight: Hybrid search beats pure vector by 24%
```

**ideas** - New concepts and opportunities
```markdown
# Idea: Voice-to-recall feature
```

**learnings** - Technical lessons learned
```markdown
# Learning: Tailwind dark mode requires dark: prefix
```

**customers** - Customer feedback and info
```markdown
# Customer: Feedback from Prague AI consulting pilot
```

**competitors** - Competitor analysis
```markdown
# Competitor: Notion AI workspace analysis
```

**research** - Market research and data
```markdown
# Research: Avatar market $117B by 2034
```

**sessions** - Session summaries and notes
```markdown
# Session: 2025-10-06 Claude Code development
```

## Tips & Tricks

### 1. Use Auto-Categorize
Let AI detect the category automatically. It's right 90%+ of the time.

### 2. Tag Liberally
```markdown
Tags: business, ai, search, performance, research, 2025
```
More tags = easier to find later.

### 3. Cross-Reference Everything
```markdown
Related to:
- [[decisions/dec-2025-10-06-001|Previous decision]]
- [[research/res-2025-10-05-002|Supporting research]]
```

### 4. Include Context
Don't just capture the decision - capture WHY.

**Bad:**
```markdown
# Decision: Use FastAPI
We chose FastAPI.
```

**Good:**
```markdown
# Decision: Use FastAPI for recall-kraliki backend

## Context
Need REST API. Evaluated Flask, Django, FastAPI.

## Decision
FastAPI - type safety, async, auto-docs, modern.

## Alternatives Rejected
- Flask: Too minimal, no async
- Django: Too heavy, ORM not needed

## Impact
Faster development, better DX, Stack 2026 compliant.
```

### 5. Review Weekly
Every Friday:
```
Click "Recent" → limit: 50
Click "Graph" → See patterns emerging
Search "learnings" → Review what you learned this week
```

### 6. Use Dark Mode
Click 🌙 button (top right) to enable dark mode.
- Saves your eyes during night sessions
- Persists across sessions
- Smooth transitions

## Keyboard Shortcuts (Coming Soon)

- `Ctrl+K` - Quick search
- `Ctrl+N` - New capture
- `Ctrl+D` - Toggle dark mode
- `/` - Focus search

## Next Steps

1. **Capture 10 items** from today's work
2. **Search for them** using different search types
3. **Create wikilinks** between related items
4. **Check the graph** to see connections
5. **Try dark mode** 🌙

**Tomorrow:** Start your day by searching recall-kraliki for context on what you're working on!

---

**Need Help?**
- Full docs: `docs/USER-GUIDE.md`
- Technical docs: `docs/CLAUDE.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
