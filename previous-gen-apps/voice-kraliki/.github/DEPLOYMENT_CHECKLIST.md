# GitHub Actions CI/CD Deployment Checklist

## Pre-Deployment Validation ✅

### Files Created
- [x] `.github/workflows/backend-tests.yml` (195 lines)
- [x] `.github/workflows/frontend-tests.yml` (244 lines)
- [x] `.github/workflows/README.md` (Documentation)
- [x] `.github/workflows/SETUP.md` (Quick start guide)
- [x] `.github/WORKFLOWS_SUMMARY.md` (Architecture overview)
- [x] `.github/DEPLOYMENT_CHECKLIST.md` (This file)

### YAML Validation
- [x] `backend-tests.yml` - Valid YAML syntax
- [x] `frontend-tests.yml` - Valid YAML syntax

### Workflow Configuration
- [x] Python 3.11 specified
- [x] Node 20.x specified
- [x] pnpm 10.14.0 specified
- [x] Coverage threshold set to 70%
- [x] Path filtering configured
- [x] Caching enabled (pip + pnpm)
- [x] Parallel test execution configured

---

## Deployment Steps

### Step 1: Commit Workflows to Repository
```bash
cd /home/adminmatej/github/applications/operator-demo-2026
git add .github/
git status
git commit -m "feat: Add GitHub Actions CI/CD workflows for automated testing

- Add backend-tests.yml with pytest, coverage (70% min), and security scanning
- Add frontend-tests.yml with TypeScript checking, Vitest, and build validation
- Include comprehensive documentation and setup guides
- Configure dependency caching for faster builds
- Enable parallel test execution
- Add PR status checks and artifact uploads

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin develop
```

**Status:** [ ] Not started | [ ] In progress | [ ] Complete

---

### Step 2: Enable GitHub Actions

1. Navigate to repository on GitHub
2. Go to **Settings** > **Actions** > **General**
3. Under "Actions permissions":
   - Select: "Allow all actions and reusable workflows"
4. Under "Workflow permissions":
   - Select: "Read and write permissions"
   - Enable: "Allow GitHub Actions to create and approve pull requests"
5. Click **Save**

**Status:** [ ] Not started | [ ] In progress | [ ] Complete

---

### Step 3: Configure Codecov (Optional but Recommended)

1. Visit [codecov.io](https://codecov.io)
2. Sign up/login with GitHub account
3. Add `operator-demo-2026` repository
4. Copy the upload token
5. In GitHub repository:
   - Go to **Settings** > **Secrets and variables** > **Actions**
   - Click **New repository secret**
   - Name: `CODECOV_TOKEN`
   - Value: (paste token)
   - Click **Add secret**

**Status:** [ ] Not started | [ ] In progress | [ ] Complete | [ ] Skipped

---

### Step 4: Set Branch Protection Rules

#### For `main` branch:

1. Go to **Settings** > **Branches**
2. Click **Add branch protection rule**
3. Branch name pattern: `main`
4. Enable the following:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (set to 1)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Search and select these status checks:
     - `Run Backend Tests with Coverage`
     - `Run Frontend Tests and Build`
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings
5. Click **Create**

**Status:** [ ] Not started | [ ] In progress | [ ] Complete

#### For `develop` branch:

Repeat the same steps as above with branch name pattern: `develop`

**Status:** [ ] Not started | [ ] In progress | [ ] Complete

---

### Step 5: Test Workflows with PR

1. Create a test feature branch:
   ```bash
   git checkout -b test/ci-cd-validation
   ```

2. Make a small change (e.g., add comment to README):
   ```bash
   echo "# Testing CI/CD workflows" >> README.md
   git add README.md
   git commit -m "test: Validate CI/CD workflows"
   git push origin test/ci-cd-validation
   ```

3. Create Pull Request on GitHub:
   - Go to **Pull requests** > **New pull request**
   - Base: `develop`, Compare: `test/ci-cd-validation`
   - Click **Create pull request**

4. Verify workflows run:
   - Check **Actions** tab
   - View running workflows
   - Verify both backend and frontend tests execute

5. Review results:
   - Check for green checkmarks
   - Review coverage reports
   - Verify PR comments appear
   - Download artifacts

**Expected Results:**
- ✅ Backend tests run and pass
- ✅ Frontend type checking passes
- ✅ Frontend build succeeds
- ✅ Coverage reports uploaded
- ✅ PR receives status comments
- ✅ Artifacts available for download

**Status:** [ ] Not started | [ ] In progress | [ ] Complete

---

### Step 6: Add Status Badges to README

1. Open main README.md
2. Add badges at the top:
   ```markdown
   # Operator Demo 2026
   
   ![Backend Tests](https://github.com/YOUR_USERNAME/operator-demo-2026/workflows/Backend%20Tests/badge.svg?branch=develop)
   ![Frontend Tests](https://github.com/YOUR_USERNAME/operator-demo-2026/workflows/Frontend%20Tests/badge.svg?branch=develop)
   [![codecov](https://codecov.io/gh/YOUR_USERNAME/operator-demo-2026/branch/develop/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/operator-demo-2026)
   ```
3. Replace `YOUR_USERNAME` with actual GitHub username
4. Commit and push

**Status:** [ ] Not started | [ ] In progress | [ ] Complete

---

## Post-Deployment Validation

### Workflow Execution Tests

#### Backend Workflow:
- [ ] Triggers on push to develop
- [ ] Triggers on PR to develop
- [ ] Python 3.11 environment set up correctly
- [ ] Pip caching works
- [ ] System dependencies install successfully
- [ ] All Python dependencies install
- [ ] Linting runs (ruff)
- [ ] Type checking runs (mypy)
- [ ] Tests execute with pytest
- [ ] Coverage reports generated
- [ ] Coverage threshold enforced (70%)
- [ ] Codecov upload succeeds
- [ ] Artifacts uploaded (HTML coverage)
- [ ] PR comment added with coverage
- [ ] Security scan completes
- [ ] Test summary generated

#### Frontend Workflow:
- [ ] Triggers on push to develop
- [ ] Triggers on PR to develop
- [ ] Node 20.x environment set up correctly
- [ ] pnpm 10.14.0 installed
- [ ] pnpm caching works
- [ ] Dependencies install with frozen lockfile
- [ ] TypeScript type checking runs
- [ ] Vitest tests run (when configured)
- [ ] Production build succeeds
- [ ] Build artifacts uploaded
- [ ] Build size reported
- [ ] Code quality checks run
- [ ] Preview build for PRs works
- [ ] PR comment added with build status
- [ ] Test summary generated

---

## Performance Metrics

### Expected Build Times (First Run):
- Backend: ~3-5 minutes
- Frontend: ~2-4 minutes

### Expected Build Times (Cached):
- Backend: ~1-2 minutes
- Frontend: ~1-2 minutes

### Cache Hit Rate:
- Target: >80% cache hits on repeat builds

**Actual Performance:**
- Backend (first run): _____ minutes
- Backend (cached): _____ minutes
- Frontend (first run): _____ minutes
- Frontend (cached): _____ minutes
- Cache hit rate: _____%

---

## Troubleshooting Reference

### Common Issues

1. **Workflow not triggering:**
   - Check Actions are enabled in Settings
   - Verify branch names match (main/develop)
   - Check path filters match changed files

2. **Coverage failing:**
   - Run locally: `pytest --cov=app --cov-report=term-missing`
   - Check which files need tests
   - Add tests to reach 70% threshold

3. **Frontend build failing:**
   - Run locally: `pnpm run build`
   - Check for TypeScript errors
   - Verify environment variables

4. **Cache not working:**
   - Check lock files haven't changed
   - Verify cache keys in workflow
   - Manually clear cache if needed

---

## Rollback Plan

If workflows cause issues:

1. **Disable workflows:**
   ```bash
   git checkout develop
   git rm .github/workflows/backend-tests.yml
   git rm .github/workflows/frontend-tests.yml
   git commit -m "temp: Disable CI/CD workflows for troubleshooting"
   git push origin develop
   ```

2. **Remove branch protection:**
   - Settings > Branches > Edit rule
   - Uncheck status check requirements
   - Save changes

3. **Fix issues locally and redeploy**

---

## Success Criteria

All items below must be checked before considering deployment successful:

### Core Functionality:
- [ ] Workflows execute on push to main/develop
- [ ] Workflows execute on PRs to main/develop
- [ ] Backend tests run successfully
- [ ] Frontend builds complete successfully
- [ ] Coverage reports generated and uploaded
- [ ] PR merge blocked when tests fail
- [ ] PR merge blocked when coverage < 70%

### Performance:
- [ ] Caching reduces build time by >50%
- [ ] Parallel tests work correctly
- [ ] Workflows complete in <5 minutes

### Integration:
- [ ] Codecov integration working (if configured)
- [ ] PR comments appear automatically
- [ ] Artifacts available for download
- [ ] Status badges display correctly

### Documentation:
- [ ] README updated with status badges
- [ ] Team informed about new CI/CD process
- [ ] Troubleshooting guide accessible

---

## Sign-Off

**Deployed by:** ________________
**Date:** ________________
**Status:** [ ] Success | [ ] Partial | [ ] Failed

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Last Updated:** October 15, 2025
**Version:** 1.0
