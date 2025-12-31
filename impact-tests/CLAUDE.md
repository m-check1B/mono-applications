# Project Memory

Project-specific context for Claude Code.

## Project Overview

- See @README.md for setup and architecture details
- Part of the GitHub workspace at /home/adminmatej/github
- Parent workspace memory: @../CLAUDE.md or @../../CLAUDE.md

## Code Style & Conventions

### Python
- Follow PEP 8, use type hints, 4-space indentation
- Import grouping: stdlib, third-party, local

### TypeScript/JavaScript/Svelte
- 2-space indentation, prefer const over let
- camelCase for functions/variables

## Development Commands

```bash
# Install dependencies
npm install  # or pip install -r requirements.txt

# Development server
npm run dev  # or python -m uvicorn app.main:app --reload

# Tests
npm test     # or pytest

# Build
npm run build
```

## Semantic Search Integration

If mgrep is available:
- Use `/mgrep "query"` for semantic code search
- See @MGREP_SELF_HOSTED_SETUP.md if available in project
- API: http://localhost:8001/v1/stores/search

## Git Workflow

- Descriptive commits in present tense ("Add feature", "Fix bug")
- Feature branches: `feature/description`
- Never commit secrets or .env files
- Include Claude co-authoring:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)
  
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

## Testing

- Run tests before committing
- Maintain test coverage
- Document test requirements

## Documentation

- Keep README updated
- Document API changes
- Add inline comments for complex logic

## Troubleshooting

### Common Issues

**Port conflicts:**
```bash
lsof -i :PORT
```

**Dependency issues:**
```bash
rm -rf node_modules && npm install  # Node
rm -rf .venv && python -m venv .venv && pip install -r requirements.txt  # Python
```

**Docker services:**
```bash
docker compose ps
docker compose logs -f [service]
docker compose restart [service]
```

---

*Update this file with project-specific conventions and commands*
*See parent @../CLAUDE.md or @../../CLAUDE.md for workspace-wide conventions*
