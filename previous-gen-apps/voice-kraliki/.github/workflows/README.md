# GitHub Actions Workflows

This directory contains CI/CD automation workflows for the Operator Demo 2026 project.

## Available Workflows

### 1. Backend Tests (`backend-tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches (when backend files change)
- Pull requests to `main` or `develop` branches (when backend files change)

**Jobs:**

#### Test Job
- **Python Version:** 3.11
- **Working Directory:** `./backend`
- **Features:**
  - Installs system dependencies (libsndfile, portaudio)
  - Caches pip packages for faster builds
  - Runs linting with `ruff` (non-blocking)
  - Runs type checking with `mypy` (non-blocking)
  - Executes pytest with parallel execution (`-n auto`)
  - Generates coverage reports (XML, HTML, terminal)
  - **Coverage Threshold:** 70% (fails if below)
  - Uploads coverage to Codecov
  - Uploads HTML coverage report as artifact (30 days retention)
  - Comments on PRs with coverage information
  - Creates test summary in GitHub Actions UI

#### Security Scan Job
- Runs `safety` check for known vulnerabilities
- Runs `bandit` security analysis on codebase
- Results are informational (non-blocking)

**Status Badges:**
```markdown
![Backend Tests](https://github.com/YOUR_USERNAME/operator-demo-2026/workflows/Backend%20Tests/badge.svg)
```

---

### 2. Frontend Tests (`frontend-tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches (when frontend files change)
- Pull requests to `main` or `develop` branches (when frontend files change)

**Jobs:**

#### Test Job
- **Node Version:** 20.x
- **Package Manager:** pnpm 10.14.0
- **Working Directory:** `./frontend`
- **Features:**
  - Installs pnpm with specific version
  - Caches pnpm store for faster builds
  - Installs dependencies with `--frozen-lockfile`
  - Runs TypeScript type checking (`pnpm run check`)
  - Runs linting (if configured)
  - Runs Vitest tests with coverage (when configured)
  - Uploads coverage to Codecov
  - Builds production bundle
  - Uploads build artifacts (7 days retention)
  - Reports build size
  - Creates test summary in GitHub Actions UI

#### Code Quality Job
- Runs Prettier format checking (if configured)
- Runs ESLint (if configured)
- TypeScript type checking

#### Build Preview Job (PRs only)
- Builds preview environment for pull requests
- Comments on PR with build status
- Provides deployment-ready artifacts

**Status Badges:**
```markdown
![Frontend Tests](https://github.com/YOUR_USERNAME/operator-demo-2026/workflows/Frontend%20Tests/badge.svg)
```

---

## Configuration

### Secrets Required

Add these secrets in your GitHub repository settings (`Settings` > `Secrets and variables` > `Actions`):

1. **CODECOV_TOKEN** (optional but recommended)
   - Get from [codecov.io](https://codecov.io)
   - Enables coverage reporting and PR comments

2. **GITHUB_TOKEN** (automatic)
   - Provided automatically by GitHub Actions
   - Used for PR comments and artifact uploads

### Branch Protection Rules

To enforce test requirements before merging:

1. Go to `Settings` > `Branches` > `Add branch protection rule`
2. For `main` and `develop` branches:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select required status checks:
     - `Run Backend Tests with Coverage`
     - `Run Frontend Tests and Build`
   - ✅ Require conversation resolution before merging

---

## Local Testing

### Backend Tests

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-fail-under=70 -v

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Frontend Tests

```bash
cd frontend

# Install dependencies
pnpm install

# Run type checking
pnpm run check

# Run tests with coverage
pnpm run test:coverage

# Run tests in UI mode
pnpm run test:ui

# Build production bundle
pnpm run build
```

---

## Troubleshooting

### Backend Tests Failing

1. **Coverage below 70%:**
   - Add more tests to increase coverage
   - Check `htmlcov/index.html` for uncovered lines

2. **Import errors:**
   - Ensure `PYTHONPATH` includes backend directory
   - Check that all dependencies are in `requirements.txt`

3. **System dependency errors:**
   - Workflow installs `libsndfile1` and `portaudio19-dev`
   - Add more system deps in the "Install system dependencies" step

### Frontend Tests Failing

1. **Type checking errors:**
   - Run `pnpm run check` locally
   - Fix TypeScript errors before pushing

2. **Build errors:**
   - Check environment variables are set correctly
   - Ensure all dependencies are in `package.json`

3. **pnpm cache issues:**
   - Cache automatically invalidates on `pnpm-lock.yaml` changes
   - Manually clear cache in GitHub Actions settings if needed

---

## Performance Optimization

### Backend
- **Parallel Testing:** Uses `pytest-xdist` with `-n auto`
- **Pip Caching:** Caches `~/.cache/pip` directory
- **Path Filtering:** Only runs on backend file changes

### Frontend
- **pnpm Store Caching:** Caches entire pnpm store
- **Frozen Lockfile:** Uses `--frozen-lockfile` for consistency
- **Path Filtering:** Only runs on frontend file changes
- **Parallel Jobs:** Runs test, lint, and preview jobs in parallel

---

## Continuous Improvement

### Adding More Checks

**Backend:**
```yaml
- name: Run security audit
  run: pip-audit
```

**Frontend:**
```yaml
- name: Check bundle size
  run: pnpm run build-stats
```

### Matrix Testing (Multiple Versions)

**Backend:**
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
```

**Frontend:**
```yaml
strategy:
  matrix:
    node-version: ['18.x', '20.x', '22.x']
```

---

## Monitoring

- **Workflow Status:** Check Actions tab in GitHub
- **Coverage Trends:** View on Codecov dashboard
- **Build Times:** Monitor in workflow run details
- **Artifact Downloads:** Available for 7-30 days

---

## Support

For issues with workflows:
1. Check workflow logs in GitHub Actions tab
2. Run tests locally to reproduce
3. Review environment configuration
4. Check secret values are set correctly

**Last Updated:** October 15, 2025
