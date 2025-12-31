# 🚀 Voice by Kraliki Replit Deployment Guide

## Overview
Voice by Kraliki is now **fully standalone** with all dependencies bundled in the `vendor/` directory. No external packages or repositories needed!

## ✅ What's Included
- All Stack 2025 packages bundled in `/vendor/packages/`
- Replit configuration files (`.replit`, `replit.nix`)
- Automatic startup script
- Database setup and seeding
- Redis configuration
- Both frontend and backend services

## 📦 Bundled Dependencies
All 19 external packages are now included:
- `@unified/auth-core`
- `@unified/telephony-core`
- `@unified/ui-core`
- `@unified/database-core`
- `@unified/config-core`
- `@unified/providers-core`
- `@unified/shared-core`
- `@stack-2025/bug-report-core`
- `@stack-2025/byok-core`
- `@stack-2025/byok-middleware`
- `@stack-2025/deepgram-agent-core`
- `@stack-2025/logger`
- `@stack-2025/polar-core`
- `@stack-2025/queue-core`
- `@stack-2025/subscription-tiers`
- `@stack-2025/testing-core`

## 🚀 Quick Deploy to Replit

### Option 1: Import from GitHub
1. Push this folder to a new GitHub repository
2. In Replit, click "Create Repl" → "Import from GitHub"
3. Paste your repository URL
4. Replit will automatically detect the configuration and start

### Option 2: Upload Directly
1. Create a new Repl (Node.js template)
2. Upload the entire `cc-lite` folder
3. The `.replit` file will configure everything automatically

## 🔧 Configuration

### 1. Database Setup (PostgreSQL)

Voice by Kraliki requires PostgreSQL. The repository now ships with an embedded PostgreSQL cluster that lives inside the project directory.

The startup script will automatically:
- Start the embedded PostgreSQL server (`pnpm db:cluster:start`)
- Create the `cc_lite` database if needed
- Run migrations
- Seed demo data

Default connection (already configured):
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cc_lite
```

**Storage location:** the database files are kept in `./.data/postgres`, so everything stays within the project workspace on Replit.

**Note**: Replit's Node.js template includes PostgreSQL binaries via `replit.nix`. If you fork the project, keep `pg_ctl`, `initdb`, `psql`, and `createdb` in the dependency list.

### 2. Required Secrets
Add these in Replit's Secrets tab:
```env
JWT_SECRET=generate_a_long_random_string_here
COOKIE_SECRET=another_long_random_string_here
```

### 3. Optional Services
Only add these if you want to use them:
```env
# AI Services
OPENAI_API_KEY=your-openai-key
DEEPGRAM_API_KEY=your-deepgram-key

# Telephony
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

### 4. Database Management
```bash
# Start / Stop the embedded Postgres service
pnpm db:cluster:start
pnpm db:cluster:status
pnpm db:cluster:stop

# View database content
pnpm db:studio

# Reset database (drops and recreates the local cluster)
pnpm db:cluster:reset

# Run migrations manually
pnpm db:migrate
```

### 3. Start Services
```bash
# Automatic (uses startup script)
bash scripts/replit-start.sh

# Or manual
pnpm dev:all  # Starts both frontend and backend
```

## 🌐 Accessing the Application

Once running, your app will be available at:
- **Frontend**: `https://[your-repl-name].[your-username].repl.co:3007`
- **Backend API**: `https://[your-repl-name].[your-username].repl.co:3010`
- **tRPC Playground**: `https://[your-repl-name].[your-username].repl.co:3010/trpc-panel`

## 📝 Test Accounts

### Default Admin
- Email: `admin@cc-light.local`
- Password: `Admin123!@#`

### Default Supervisor
- Email: `supervisor@cc-light.local`
- Password: `Supervisor123!@#`

### Default Agent
- Email: `agent1@cc-light.local`
- Password: `Agent123!@#`

## 🛠️ Available Commands

```bash
# Development
pnpm dev           # Start frontend only
pnpm dev:server    # Start backend only
pnpm dev:all       # Start both

# Building
pnpm build         # Build for production

# Database
pnpm db:migrate    # Run migrations
pnpm db:seed       # Seed demo data
pnpm db:studio     # Open Prisma Studio

# Testing
pnpm test          # Run tests
pnpm test:e2e      # Run E2E tests
```

## ⚠️ Production Considerations

Before deploying to production:

1. **Change all secrets** in environment variables
2. **Disable demo users** by setting `SEED_DEMO_USERS=false`
3. **Configure proper SSL** certificates
4. **Set up proper database** (not SQLite)
5. **Configure Redis** with persistence
6. **Enable monitoring** (Sentry, etc.)
7. **Set `NODE_ENV=production`**

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill existing processes
pkill -f "node"
pkill -f "vite"
```

### Database Connection Issues
```bash
# Restart PostgreSQL
pg_ctl restart

# Check connection
psql -U postgres -d cc_lite -c "SELECT 1"
```

### Missing Dependencies
```bash
# Clean install
rm -rf node_modules
pnpm install
```

### Build Errors
```bash
# Clear build cache
rm -rf dist .vite
pnpm build
```

## 📄 License
This is a standalone version of Voice by Kraliki prepared for deployment. Check LICENSE file for details.

## 🤝 Support
For issues specific to Replit deployment, check the logs in the Replit console or contact support.

---

**Note**: This is a beta version. Some features may still be in development.
