# Git Push Instructions for CC-Lite 2026

**Date:** November 10, 2025
**Remote:** https://github.com/m-check1B/cc-lite-2026.git
**Status:** Ready to push (authentication required)

---

## Current Status

✅ **Repository prepared:**
- Remote updated to: `https://github.com/m-check1B/cc-lite-2026.git`
- All changes committed (3 commits ahead)
- Main branch ready
- Develop branch ready

❌ **Needs authentication:**
- GitHub repository access required
- Personal access token or SSH key needed

---

## Step 1: Create Repository on GitHub (if not exists)

### Option A: Via GitHub Web Interface
1. Go to https://github.com/m-check1B
2. Click "New repository"
3. Repository name: `cc-lite-2026`
4. Description: "CC-Lite 2026 - Professional AI Call Center Platform"
5. Visibility: Private (recommended) or Public
6. **DO NOT** initialize with README, .gitignore, or license
7. Click "Create repository"

### Option B: Via GitHub CLI
```bash
gh repo create m-check1B/cc-lite-2026 \
  --private \
  --description "CC-Lite 2026 - Professional AI Call Center Platform" \
  --source=.
```

---

## Step 2: Setup Authentication

### Option A: Personal Access Token (Recommended)

1. **Generate Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Note: "CC-Lite 2026 Push Access"
   - Expiration: 90 days (or custom)
   - Select scopes:
     - ✅ `repo` (Full control of private repositories)
   - Click "Generate token"
   - **COPY THE TOKEN** (you won't see it again!)

2. **Configure Git to Use Token:**
   ```bash
   # Store token in git credential helper
   git config --global credential.helper store

   # First push will prompt for credentials
   # Username: m-check1B
   # Password: <paste your token>
   ```

### Option B: SSH Key (Alternative)

1. **Generate SSH Key** (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

2. **Add to GitHub:**
   ```bash
   # Copy public key
   cat ~/.ssh/id_ed25519.pub

   # Add at: https://github.com/settings/keys
   ```

3. **Update Remote to Use SSH:**
   ```bash
   git remote set-url origin git@github.com:m-check1B/cc-lite-2026.git
   ```

---

## Step 3: Push to GitHub

Once authentication is configured:

```bash
# Currently on main branch
git push -u origin main

# Switch to develop and push
git checkout develop
git push -u origin develop

# Verify both branches pushed
git branch -a
```

Expected output:
```
* develop
  main
  remotes/origin/develop
  remotes/origin/main
```

---

## Step 4: Set Develop as Default Branch

### Via GitHub Web Interface:
1. Go to: https://github.com/m-check1B/cc-lite-2026
2. Click "Settings" tab
3. Click "Branches" in left sidebar
4. Under "Default branch":
   - Click the switch icon next to "main"
   - Select "develop"
   - Click "Update"
   - Confirm by clicking "I understand, update the default branch"

### Via GitHub CLI:
```bash
gh repo edit m-check1B/cc-lite-2026 --default-branch develop
```

---

## Step 5: Verify Setup

```bash
# Check remote and branches
git remote -v
git branch -a

# Fetch to verify
git fetch origin

# Should show:
# * [new branch]      develop -> origin/develop
# * [new branch]      main -> origin/main
```

---

## Repository Structure After Push

```
cc-lite-2026/
├── main (branch)
│   └── Production-ready code (90/100 score)
│       - No promotion files yet
│       - Original operator-demo state
│
└── develop (default branch)
    └── Active development
        - Promotion files (PROMOTION_PLAN.md, FEATURE_ROADMAP.md)
        - Updated README
        - Embedded reference (_cc-lite-reference/)
        - 3 commits ahead of main
```

---

## Branch Protection Rules (Recommended)

After pushing, configure branch protection:

### For `main` branch:
1. Go to: https://github.com/m-check1B/cc-lite-2026/settings/branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Settings:
   - ✅ Require pull request reviews before merging (1 approval)
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators
5. Click "Create"

### For `develop` branch:
1. Branch name pattern: `develop`
2. Settings:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
3. Click "Create"

---

## Workflow After Setup

### Feature Development:
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/campaign-management

# Make changes, commit
git add .
git commit -m "feat: implement campaign management"

# Push feature branch
git push -u origin feature/campaign-management

# Create PR on GitHub: feature/campaign-management → develop
```

### Release to Production:
```bash
# When develop is stable
# Create PR on GitHub: develop → main
# After merge:

git checkout main
git pull origin main
git tag -a v2.0.0 -m "Release: CC-Lite 2026 v2.0.0"
git push origin v2.0.0
```

---

## Current Commits Ready to Push

### develop branch (3 commits):
```
43840a5 feat: add embedded cc-lite reference template
f7cd1c7 feat: promote operator-demo-2026 → cc-lite-2026 as production app
496860b feat(security): Add comprehensive Redis security incident report
```

### main branch:
```
f3f0f89 feat: Add comprehensive test coverage infrastructure
bb5248b Refactor code structure for improved readability
992e53f feat: Add API services, session synchronization
```

---

## Troubleshooting

### "Authentication failed"
- **Solution:** Generate and use Personal Access Token (see Step 2A above)
- Or configure SSH key (see Step 2B above)

### "Repository not found"
- **Solution:** Create the repository first (see Step 1)
- Verify URL is correct: `https://github.com/m-check1B/cc-lite-2026.git`

### "Permission denied"
- **Solution:** Ensure you have write access to m-check1B/cc-lite-2026
- Check token has `repo` scope

### "Branch protection rules prevent push"
- **Solution:** Push protection is configured after first push
- For now, just push without rules (configure later in Step 5)

---

## Quick Reference Commands

```bash
# Setup (one-time)
git remote add origin https://github.com/m-check1B/cc-lite-2026.git

# Push main
git checkout main
git push -u origin main

# Push develop
git checkout develop
git push -u origin develop

# Set default branch (via GitHub web or CLI)
gh repo edit m-check1B/cc-lite-2026 --default-branch develop

# Verify
git remote -v
git branch -a
```

---

## Next Steps After Push

1. ✅ Verify both branches on GitHub
2. ✅ Set develop as default branch
3. ✅ Configure branch protection rules (optional)
4. ✅ Add repository description and topics
5. ✅ Update repository settings (Issues, Projects, Wiki)
6. 🚀 Start implementing Campaign Management (Week 1-2)

---

**Ready to push?**
1. Create/verify repository exists
2. Setup authentication (token or SSH)
3. Run push commands above
4. Set develop as default
5. Start developing!

See [PROMOTION_PLAN.md](./PROMOTION_PLAN.md) and [FEATURE_ROADMAP.md](./FEATURE_ROADMAP.md) for next steps.
