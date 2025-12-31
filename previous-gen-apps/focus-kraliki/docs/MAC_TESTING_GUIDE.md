# Mac Testing Guide for Focus by Kraliki

> **Purpose:** Cookbook for local development and testing on macOS, including Stripe payment testing.

---

## 1. Prerequisites

### System Requirements

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| macOS | 12.0+ (Monterey or later) | `sw_vers` |
| Node.js | 24.0+ | `node --version` |
| pnpm | 10.0+ | `pnpm --version` |
| Python | 3.13+ | `python3 --version` |
| uv | Latest | `uv --version` |
| PostgreSQL | 15+ | `psql --version` |
| Docker | Latest (optional) | `docker --version` |

### Install Prerequisites

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js (v24+)
brew install node@24
# Or use nvm:
nvm install 24
nvm use 24

# Install pnpm
npm install -g pnpm@10

# Install Python 3.13+
brew install python@3.13

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Docker (optional, for containerized setup)
brew install --cask docker
```

### Required API Keys

For full functionality, you'll need:

| Service | Purpose | Get Key From |
|---------|---------|--------------|
| Anthropic | Claude AI | https://console.anthropic.com/ |
| OpenAI | GPT-4 | https://platform.openai.com/ |
| Stripe | Payments | https://dashboard.stripe.com/ |
| Deepgram | Voice transcription (optional) | https://console.deepgram.com/ |
| Gemini | File search (optional) | https://aistudio.google.com/ |

---

## 2. Local Setup Steps

### Step 1: Clone and Navigate

```bash
# If working from the main repository
cd /path/to/github/applications/focus-kraliki

# Or clone directly
git clone <repository-url>
cd focus-kraliki
```

### Step 2: Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Copy environment template
cp .env.example .env

# Edit .env with your configuration (see section below)
nano .env  # or use your preferred editor

# Install Python dependencies with uv
uv sync

# Run database migrations
uv run alembic upgrade head
```

### Step 3: Configure Environment Variables

Edit `backend/.env` with your settings:

```bash
# Database (create database first: createdb focus_kraliki)
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5432/focus_kraliki

# AI Services (add your keys)
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...

# Stripe (TEST MODE keys - use test keys!)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_MONTHLY=price_...
STRIPE_PRICE_ID_YEARLY=price_...

# Auth
JWT_SECRET=your-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Server (ALWAYS use 127.0.0.1, never 0.0.0.0)
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
DEBUG=true

# CORS (match your frontend port)
ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
STATIC_FILE_BASE_URL=http://127.0.0.1:8000/static  # Optional
II_AGENT_WEBHOOK_SECRET=local-dev-webhook-secret
GOOGLE_CALENDAR_WEBHOOK_TOKEN=optional-token
```

### Step 4: Set Up Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Copy environment template
cp .env.example .env

# Edit frontend .env
echo 'PUBLIC_API_URL=http://127.0.0.1:8000' > .env
# PUBLIC_API_URL is required and must include http(s)

# Install dependencies with pnpm
pnpm install
```

### Step 5: Create PostgreSQL Database

```bash
# Create the database
createdb focus_kraliki

# Or via psql
psql -c "CREATE DATABASE focus_kraliki;"

# Verify connection
psql -d focus_kraliki -c "SELECT 1;"
```

---

## 3. How to Run Frontend and Backend

### Option A: Using Dev Scripts (Recommended)

The repository includes convenience scripts for development:

```bash
# From project root
cd /path/to/focus-kraliki

# Start both services (automatically clears ports)
./dev-start.sh

# Stop all services
./dev-stop.sh
```

**Services will be available at:**
- Backend API: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs
- Frontend: http://127.0.0.1:5173

### Option B: Manual Start (Separate Terminals)

**Terminal 1 - Backend:**
```bash
cd backend

# Using uv (recommended)
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Or with PYTHONPATH set
PYTHONPATH=. uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
pnpm dev
# Frontend runs on http://127.0.0.1:5173
```

### Option C: Using Docker Compose

```bash
# Start with Docker (binds to localhost only)
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Health Check

Verify services are running:

```bash
# Backend health
curl http://127.0.0.1:8000/health

# Frontend (should return HTML)
curl -s http://127.0.0.1:5173 | head -20
```

---

## 4. Testing Stripe Payments on Mac

### Step 1: Set Up Stripe Test Mode

1. **Go to Stripe Dashboard:** https://dashboard.stripe.com/test/dashboard
2. **Ensure Test Mode is ON** (toggle in top-right corner)
3. **Get your test keys:**
   - API Keys page: https://dashboard.stripe.com/test/apikeys
   - Copy `Publishable key` (pk_test_...)
   - Copy `Secret key` (sk_test_...)

### Step 2: Create Test Products and Prices

In Stripe Dashboard (Test Mode):

1. Go to **Products** > **Add Product**
2. Create two products:
   - **Pro Monthly:** $9.00/month
   - **Pro Yearly:** $79.00/year
3. Copy the `price_...` IDs for each product
4. Add to your `.env`:
   ```bash
   STRIPE_PRICE_ID_MONTHLY=price_1234...
   STRIPE_PRICE_ID_YEARLY=price_5678...
   ```

### Step 3: Set Up Stripe Webhook (Local Testing)

Install and run Stripe CLI for local webhook testing:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe (opens browser)
stripe login

# Forward webhooks to local backend
stripe listen --forward-to http://127.0.0.1:8000/billing/webhook

# Copy the webhook signing secret (whsec_...) displayed
# Add to .env:
# STRIPE_WEBHOOK_SECRET=whsec_...
```

Keep the `stripe listen` command running in a separate terminal while testing.

### Step 4: Test Payment Flow

1. **Start the application** (backend + frontend)

2. **Register/Login** to Focus by Kraliki

3. **Navigate to Settings/Billing**

4. **Initiate checkout:**
   - Click "Upgrade to Pro" or similar
   - Select monthly or yearly plan
   - You'll be redirected to Stripe Checkout

5. **Use Stripe Test Cards:**

   | Card Number | Result |
   |-------------|--------|
   | `4242 4242 4242 4242` | Success |
   | `4000 0000 0000 3220` | Requires 3D Secure |
   | `4000 0000 0000 9995` | Declined (insufficient funds) |
   | `4000 0000 0000 0002` | Generic decline |

   - **Expiry:** Any future date (e.g., 12/34)
   - **CVC:** Any 3 digits (e.g., 123)
   - **ZIP:** Any 5 digits (e.g., 12345)

6. **Verify webhook events** in the `stripe listen` terminal

7. **Check subscription status:**
   ```bash
   curl http://127.0.0.1:8000/billing/subscription-status \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

### Step 5: Test Stripe Customer Portal

```bash
# Get portal session URL
curl -X GET "http://127.0.0.1:8000/billing/portal-session" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Open the returned URL in browser to manage subscription
```

### Step 6: Test Subscription Cancellation

```bash
# Cancel subscription
curl -X POST "http://127.0.0.1:8000/billing/cancel-subscription" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Reactivate subscription
curl -X POST "http://127.0.0.1:8000/billing/reactivate-subscription" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 5. Common Issues and Solutions

### Issue: Port Already in Use

**Symptom:** `Address already in use` error

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use the dev-stop script
./dev-stop.sh
```

### Issue: Database Connection Failed

**Symptom:** `could not connect to server` or `database "focus_kraliki" does not exist`

**Solution:**
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL if stopped
brew services start postgresql@15

# Create database if missing
createdb focus_kraliki

# Verify connection
psql -d focus_kraliki -c "SELECT 1;"
```

### Issue: Node Version Mismatch

**Symptom:** `The engine "node" is incompatible with this module`

**Solution:**
```bash
# Check current version
node --version

# Install correct version with nvm
nvm install 24
nvm use 24

# Verify
node --version  # Should show v24.x.x
```

### Issue: pnpm Not Found

**Symptom:** `command not found: pnpm`

**Solution:**
```bash
# Install pnpm globally
npm install -g pnpm@10

# Or with corepack (Node.js 16.9+)
corepack enable
corepack prepare pnpm@10 --activate
```

### Issue: Python/uv Issues

**Symptom:** `uv: command not found` or Python version mismatch

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell
source ~/.zshrc  # or ~/.bashrc

# Verify Python version
python3 --version  # Should be 3.13+

# If wrong version, use pyenv
brew install pyenv
pyenv install 3.13
pyenv global 3.13
```

### Issue: Stripe Webhook Not Receiving Events

**Symptom:** Payments succeed but user status doesn't update

**Solution:**
```bash
# Ensure stripe listen is running
stripe listen --forward-to http://127.0.0.1:8000/billing/webhook

# Check the webhook secret matches
echo $STRIPE_WEBHOOK_SECRET

# Test webhook manually
stripe trigger checkout.session.completed
```

### Issue: CORS Errors

**Symptom:** Browser console shows CORS errors

**Solution:**
1. Check `ALLOWED_ORIGINS` in backend `.env`:
   ```bash
   ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
   ```
2. Restart backend after changing `.env`
3. Clear browser cache

### Issue: JWT Token Expired/Invalid

**Symptom:** `401 Unauthorized` on API calls

**Solution:**
```bash
# Re-login to get fresh token
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"your-password"}'

# Use the new token in subsequent requests
```

### Issue: Alembic Migration Errors

**Symptom:** `alembic upgrade head` fails

**Solution:**
```bash
# Check current migration status
uv run alembic current

# If corrupted, reset migrations (DANGER: loses data)
dropdb focus_kraliki
createdb focus_kraliki
uv run alembic upgrade head
```

---

## Quick Reference

### Essential Commands

```bash
# Start development
./dev-start.sh

# Stop development
./dev-stop.sh

# Run backend only
cd backend && uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Run frontend only
cd frontend && pnpm dev

# Run tests
cd backend && uv run pytest

# Database migrations
cd backend && uv run alembic upgrade head

# Stripe webhook forwarding
stripe listen --forward-to http://127.0.0.1:8000/billing/webhook
```

### Service URLs (Development)

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:5173 |
| Backend API | http://127.0.0.1:8000 |
| API Docs (Swagger) | http://127.0.0.1:8000/docs |
| API Docs (ReDoc) | http://127.0.0.1:8000/redoc |

### Stripe Test Cards

| Card | Scenario |
|------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 3220` | 3D Secure required |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0027 6000 3184` | Requires authentication |

---

## Additional Resources

- [Focus by Kraliki README](/home/adminmatej/github/applications/focus-kraliki/README.md)
- [Database Setup Guide](/home/adminmatej/github/applications/focus-kraliki/docs/DATABASE_SETUP.md)
- [Scripts Guide](/home/adminmatej/github/applications/focus-kraliki/docs/SCRIPTS.md)
- [Stripe Testing Documentation](https://stripe.com/docs/testing)
- [Stripe CLI Reference](https://stripe.com/docs/stripe-cli)

---

*Last Updated: 2025-12-21*
*Document ID: VD-161*
