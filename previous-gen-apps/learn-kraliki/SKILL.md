# Learn by Kraliki - Skill File

## Overview

Learn by Kraliki is a business-focused Learning Management System (LMS) for:
- Client onboarding courses
- AI Academy training (revenue stream)
- Product documentation
- Progress tracking

## Capabilities

### Course Management
- List available courses
- Get course details with lessons
- Serve markdown lesson content
- Track user progress

### Content System
- Markdown-based lessons
- JSON course metadata
- File-based storage (easy to edit)
- Supports code blocks, tables, quotes

### Progress Tracking
- Per-user, per-course progress
- Lesson completion status
- Percentage complete
- Completion timestamps

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/courses` | GET | List all courses |
| `/api/courses/{slug}` | GET | Get course details |
| `/api/courses/{slug}/lessons/{id}` | GET | Get lesson content |
| `/api/progress` | GET | List user progress |
| `/api/progress/{course}` | GET | Course progress |
| `/api/progress/{course}/{lesson}` | POST | Mark complete |

## Integration Points

### Kraliki Swarm Dashboard
- Feature in Swarm dashboard navigation
- SSO via Zitadel (planned)
- Embedded iframe support

### MCP Tools
- `learn_list_courses` - List available courses
- `learn_get_course` - Get course details
- `learn_get_progress` - Check user progress
- `learn_mark_complete` - Mark lesson done

## Tech Stack

- **Frontend**: SvelteKit 5 + TypeScript + Tailwind CSS 4
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Content**: Markdown files with JSON metadata
- **Auth**: Zitadel SSO (planned)

## Port Assignment

- Backend: 8030
- Frontend Dev: 5176
- Database: 5436 (PostgreSQL)

## Content Structure

```
content/
├── course-slug/
│   ├── course.json      # Metadata
│   ├── 01-lesson.md     # Lesson 1
│   ├── 02-lesson.md     # Lesson 2
│   └── ...
```

### course.json Schema

```json
{
  "title": "Course Title",
  "description": "Course description",
  "level": "beginner|intermediate|advanced",
  "duration_minutes": 30,
  "is_free": true,
  "lessons": ["01-intro.md", "02-basics.md"],
  "author": "Author Name",
  "tags": ["tag1", "tag2"]
}
```

## Events

| Event | Trigger |
|-------|---------|
| `course.started` | User starts a course |
| `lesson.completed` | User completes a lesson |
| `course.completed` | All lessons done |

## Development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8030

# Frontend
cd frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | true | Enable debug mode |
| `HOST` | 127.0.0.1 | Bind address |
| `PORT` | 8030 | Backend port |
| `DATABASE_URL` | sqlite://... | Database connection |
| `CONTENT_DIR` | ./content | Course content path |
