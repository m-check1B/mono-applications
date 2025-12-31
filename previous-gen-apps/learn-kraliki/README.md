# Learn by Kraliki

Business-focused Learning Management System (LMS) for Verduona products and AI Academy.

========================================
ONE PRODUCT / ONE ENGINE / MANY TEMPLATES
Learn is delivered as a Swarm feature page; standalone is optional.
========================================

## Features

- **Course Catalog** - Browse available courses
- **Course Viewer** - Read markdown lessons with prev/next navigation
- **Progress Tracking** - Track completion per user
- **AI Academy** - Revenue stream through paid AI training courses

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8030
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up -d
```

## Tech Stack

- **Frontend**: SvelteKit 5 + TypeScript + Tailwind CSS 4
- **Backend**: FastAPI + PostgreSQL
- **Content**: Markdown-based lessons

## Course Content

Courses are stored in the `/content` directory:

```
content/
├── getting-started/
│   ├── course.json          # Course metadata
│   ├── 01-welcome.md
│   ├── 02-dashboard-tour.md
│   └── 03-first-steps.md
└── ai-fundamentals/
    ├── course.json
    ├── 01-what-is-ai.md
    └── 02-ai-applications.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/courses` | List all courses |
| GET | `/api/courses/{slug}` | Get course details |
| GET | `/api/courses/{slug}/lessons/{id}` | Get lesson content |
| GET | `/api/progress` | Get user progress |
| POST | `/api/progress/{course}/{lesson}` | Mark lesson complete |

## Integration

Learn is a **Dashboard Feature** in the Kraliki ecosystem:
- Embedded in Kraliki at `/learn`
- Accessible standalone via learn.kraliki.com (prod) and learn.verduona.dev (dev)
- Supports MCP access for agents
- SSO via Zitadel (planned)

**Template-first:** Learn is delivered as a Swarm feature page by default; standalone is optional.

## Revenue Model

| Course | Price | Status |
|--------|-------|--------|
| Getting Started | Free | MVP |
| AI Academy L1 | Free | Lead gen |
| AI Academy L2 | EUR 497 | Planned |
| AI Academy L3 | EUR 997 | Planned |
| AI Academy L4 | EUR 1,997 | Planned |

## License

Proprietary - Verduona d.o.o.
