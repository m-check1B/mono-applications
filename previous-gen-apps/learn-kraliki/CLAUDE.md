# Learn by Kraliki - Project Memory

> **SECURITY: DEV SERVER ON INTERNET. NEVER bind to `0.0.0.0`. Always use `127.0.0.1`. See `/github/CLAUDE.md`.**

Business-focused Learning Management System (LMS) integrated into Kraliki.

**Skill Reference:** See `SKILL.md` for capabilities, architecture, and integration details.

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Learn is delivered as a Swarm feature page by default.
Standalone app is optional when required.
========================================

## Project Overview

Learn by Kraliki provides:
- Client onboarding courses ("Getting Started with Kraliki")
- AI Academy training modules (L1-L4 content, revenue stream)
- Product documentation with interactive tutorials
- Progress tracking per user

**Tech Stack:**
- Backend: FastAPI + PostgreSQL
- Frontend: SvelteKit 5 + Tailwind CSS 4
- Content: Markdown-based lessons
- Design: Modern Brutalism (style-2026)

## Key Directories

```
learn-kraliki/
├── frontend/src/
│   ├── routes/           # Pages
│   │   ├── +page.svelte  # Course catalog
│   │   └── courses/[slug]/ # Course viewer
│   └── lib/
│       ├── api/          # API client
│       ├── stores/       # Auth, progress stores
│       └── components/   # Reusable UI
│
├── backend/app/
│   ├── core/             # Config, auth, database
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── routers/          # API endpoints
│   └── services/         # Business logic
│
└── content/              # Course content (markdown)
    ├── getting-started/
    │   ├── course.json   # Course metadata
    │   ├── 01-welcome.md
    │   └── ...
    └── ai-fundamentals/
        ├── course.json
        └── ...
```

## Development Commands

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8030

# Frontend
cd frontend
npm install
npm run dev

# Docker
docker compose up -d
```

## API Structure

- `/api/courses` - List all courses
- `/api/courses/{slug}` - Get course details
- `/api/courses/{slug}/lessons/{lesson}` - Get lesson content
- `/api/progress` - User progress tracking
- `/api/progress/{course_slug}` - Course progress

## Key Features

1. **Course Catalog** - Browse available courses
2. **Course Viewer** - Markdown lesson rendering with navigation
3. **Progress Tracking** - Track completion per user
4. **Sample Content** - Getting Started + AI Fundamentals preview

## Content Structure

Each course has:
- `course.json` - Metadata (title, description, lessons list)
- `XX-lesson-name.md` - Lesson content in markdown

## Design Patterns

- Content stored as files (easy to edit)
- Progress stored in database (per user)
- Courses can be free or paid (via Stripe integration later)

## Port Assignment

- **Backend API**: 8030
- **Frontend Dev**: 5176

## Events Published

```python
course.started
lesson.completed
course.completed
```

---

*Part of the GitHub workspace at /home/adminmatej/github*
*See parent @../../../CLAUDE.md for workspace conventions*
