# GitHub Actions CI/CD - Quick Reference Card

## File Locations

```
/home/adminmatej/github/applications/operator-demo-2026/
└── .github/
    ├── workflows/
    │   ├── backend-tests.yml       ← Backend CI/CD workflow
    │   ├── frontend-tests.yml      ← Frontend CI/CD workflow
    │   ├── README.md               ← Full documentation
    │   └── SETUP.md                ← Quick start guide
    ├── WORKFLOWS_SUMMARY.md        ← Architecture overview
    ├── DEPLOYMENT_CHECKLIST.md     ← Deployment steps
    └── QUICK_REFERENCE.md          ← This file
```

---

## Workflow Triggers

Both workflows run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Only when relevant files change (path filtering)

---

## Backend Workflow

**File:** `.github/workflows/backend-tests.yml`

### What It Does
- Sets up Python 3.11 environment
- Installs dependencies from `requirements.txt`
- Runs pytest with coverage (must be ≥70%)
- Executes security scans (safety, bandit)
- Uploads coverage reports to Codecov
- Blocks PR merge if tests fail

### Local Testing
```bash
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-fail-under=70 -v
```

### Key Jobs
1. **test** - Main testing job (BLOCKS PR)
2. **security-scan** - Vulnerability scanning (informational)

---

## Frontend Workflow

**File:** `.github/workflows/frontend-tests.yml`

### What It Does
- Sets up Node.js 20.x with pnpm 10.14.0
- Installs dependencies with frozen lockfile
- Runs TypeScript type checking
- Executes Vitest tests (when configured)
- Builds production bundle
- Blocks PR merge if build fails

### Local Testing
```bash
cd frontend
pnpm install
pnpm run check
pnpm run test:coverage
pnpm run build
```

### Key Jobs
1. **test** - Testing and build (BLOCKS PR)
2. **lint-and-format** - Code quality (BLOCKS PR)
3. **build-preview** - PR preview builds (informational)

---

## Common Commands

### Deploy Workflows
```bash
cd /home/adminmatej/github/applications/operator-demo-2026
git add .github/
git commit -m "feat: Add GitHub Actions CI/CD workflows"
git push origin develop
```

### Test Locally Before Pushing
```bash
# Backend
cd backend && pytest --cov=app --cov-fail-under=70 -v

# Frontend
cd frontend && pnpm run check && pnpm run build
```

### Validate YAML Syntax
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/backend-tests.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/frontend-tests.yml'))"
```

---

## PR Merge Requirements

### Backend
- All tests must pass
- Code coverage ≥ 70%
- Security scan completes (findings allowed)

### Frontend
- TypeScript type checking passes
- Production build succeeds
- Tests pass (when configured)

---

## Performance Features

### Caching
- Backend: pip packages (~2-3 min faster)
- Frontend: pnpm store (~1-2 min faster)

### Parallel Execution
- Backend: pytest -n auto
- Frontend: Multiple jobs in parallel

### Path Filtering
- Backend: Only runs when `backend/**` files change
- Frontend: Only runs when `frontend/**` files change

---

## Artifacts & Reports

### Backend
- Coverage HTML report (30 days retention)
- Coverage XML for Codecov
- Security scan results

### Frontend
- Production build (7 days retention)
- Coverage reports (30 days retention)
- Build size metrics

---

## Required GitHub Secrets

### Mandatory
- `GITHUB_TOKEN` - Auto-provided by GitHub

### Optional
- `CODECOV_TOKEN` - For Codecov integration
  - Get from: https://codecov.io
  - Add in: Settings > Secrets and variables > Actions

---

## Branch Protection Setup

1. Go to **Settings** > **Branches**
2. Add rule for `main` and `develop`
3. Enable:
   - Require status checks to pass before merging
   - Select: `Run Backend Tests with Coverage`
   - Select: `Run Frontend Tests and Build`

---

## Troubleshooting Quick Fixes

### Workflow Not Running
```bash
# Check Actions are enabled
Repository Settings → Actions → General → Allow all actions
```

### Coverage Below 70%
```bash
cd backend
pytest --cov=app --cov-report=term-missing
# Check output for uncovered lines
# Add tests to increase coverage
```

### Frontend Build Failing
```bash
cd frontend
pnpm run check  # Check TypeScript errors
pnpm run build  # Test build locally
```

### Cache Not Working
```bash
# Cache invalidates when lock files change
# Manually clear: Settings → Actions → Caches
```

---

## Status Badges

Add to README.md:
```markdown
![Backend Tests](https://github.com/YOUR_USERNAME/operator-demo-2026/workflows/Backend%20Tests/badge.svg?branch=develop)
![Frontend Tests](https://github.com/YOUR_USERNAME/operator-demo-2026/workflows/Frontend%20Tests/badge.svg?branch=develop)
```

---

## Expected Build Times

### First Run (No Cache)
- Backend: 3-5 minutes
- Frontend: 2-4 minutes

### Cached Runs
- Backend: 1-2 minutes
- Frontend: 1-2 minutes

---

## Documentation Files

- **Full Docs:** `.github/workflows/README.md`
- **Setup Guide:** `.github/workflows/SETUP.md`
- **Architecture:** `.github/WORKFLOWS_SUMMARY.md`
- **Deployment:** `.github/DEPLOYMENT_CHECKLIST.md`
- **Quick Ref:** `.github/QUICK_REFERENCE.md` (this file)

---

## Emergency Rollback

If workflows cause critical issues:
```bash
git checkout develop
git rm .github/workflows/backend-tests.yml
git rm .github/workflows/frontend-tests.yml
git commit -m "temp: Disable CI/CD workflows"
git push origin develop
```

Then remove branch protection requirements in Settings.

---

## Support Resources

- GitHub Actions Docs: https://docs.github.com/actions
- pytest Documentation: https://docs.pytest.org
- Vitest Documentation: https://vitest.dev
- Codecov Documentation: https://docs.codecov.com

---

**Last Updated:** October 15, 2025
**Quick Access:** Keep this file bookmarked for fast reference
