# Learn by Kraliki - Course Content

This directory contains all course content for the Learn by Kraliki platform.

## Course Catalog

| Course | Level | Lessons | Price | Status |
|--------|-------|---------|-------|--------|
| Getting Started | Beginner | 3 | Free | Live |
| AI Fundamentals (L1) | Beginner | 13 | EUR 49 | Live |
| AI Pro (L2) | Intermediate | 10 | EUR 199 | Coming Feb 2026 |
| AI-First Founder (L4) | Advanced | 12 | EUR 3,000+ | Coming Mar 2026 |

## Directory Structure

```
content/
├── getting-started/          # Free onboarding course
│   ├── course.json           # Course metadata
│   ├── 01-welcome.md
│   ├── 02-dashboard-tour.md
│   └── 03-first-steps.md
│
├── ai-fundamentals/          # L1: The New Reality (EUR 49)
│   ├── course.json
│   ├── 01-the-black-box.md      # Module 1: The New Reality
│   ├── 02-search-vs-reasoning.md
│   ├── 03-overcoming-fear.md
│   ├── 04-rtc-framework.md      # Module 2: Speaking Machine
│   ├── 05-iteration-and-context.md
│   ├── 06-exercise-perfect-prompt.md
│   ├── 07-email-assistant.md    # Module 3: Everyday Magic
│   ├── 08-knowledge-buffer.md
│   ├── 09-creative-spark.md
│   ├── 10-study-buddy.md
│   ├── 11-hallucinations.md     # Module 4: Safety First
│   ├── 12-data-privacy.md
│   └── 13-final-assessment.md
│
├── prompt-engineering/       # L2: AI Pro (EUR 199) - Preview only
│   ├── course.json
│   └── 01-the-toolbelt.md
│
└── ai-architecture/          # L4: AI-First Founder (EUR 3,000+) - Preview only
    ├── course.json
    └── 01-ocelot-model-intro.md
```

## Course JSON Schema

Each course has a `course.json` with:

```json
{
  "slug": "course-slug",
  "title": "Course Title",
  "description": "Course description...",
  "level": "beginner|intermediate|advanced",
  "duration_minutes": 120,
  "is_free": false,
  "price_eur": 49,
  "lessons": [
    {
      "id": "01-lesson-slug",
      "title": "Lesson Title",
      "order": 1,
      "module": 1,
      "module_name": "Module Name"
    }
  ],
  "author": "Team Name",
  "tags": ["tag1", "tag2"],
  "academy_level": "L1|L2|L4",
  "learning_outcomes": ["Outcome 1", "Outcome 2"],
  "certification": "Certificate Name"
}
```

## Content Source

This content was consolidated from:

1. `/github/brain-2026/academy/` - Curriculum documents
   - L1-CURRICULUM-DETAILED.md
   - L1-STUDENT-CURRICULUM.md
   - L2-PRO-CURRICULUM.md
   - L4-BUSINESS-GURU-CURRICULUM.md

2. `/github/marketing-2026/content/academy/` - Marketing copy
   - ACADEMY-L1-Description.md
   - ACADEMY-L1-MODULE-TEASERS.md
   - level-1-scripts/ (video scripts)

Original files retained in source locations for reference.

## Adding New Content

1. Create course directory: `content/[course-slug]/`
2. Add `course.json` with metadata
3. Add lesson files: `01-lesson-name.md`, `02-lesson-name.md`, etc.
4. Lesson IDs in course.json must match filenames (without .md extension)

## Lesson Markdown Format

Each lesson should include:

- H1 title matching lesson title
- Introduction paragraph
- Structured content with H2/H3 headers
- Tables, code blocks, lists as appropriate
- "What's Next?" section linking to next lesson
- Module/lesson footer

---

*Last updated: 2025-12-27*
*Content consolidated by AI Academy Team*
