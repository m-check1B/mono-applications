#!/bin/bash

echo "🚀 Starting Voice by Kraliki on Replit..."
echo "================================"

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env

    # Update Replit-specific values
    if [ -n "$REPL_SLUG" ] && [ -n "$REPL_OWNER" ]; then
        sed -i "s|your-repl-name|$REPL_SLUG|g" .env
        sed -i "s|your-username|$REPL_OWNER|g" .env
    fi

    # Set PostgreSQL as default
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cc_lite|g" .env
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies with pnpm..."
    pnpm install
fi

# Setup PostgreSQL (stored inside the project workspace)
echo "🐘 Starting embedded PostgreSQL service..."

if command -v pg_ctl &> /dev/null; then
    pnpm db:cluster:start || {
        echo "❌ Failed to start PostgreSQL"
        exit 1
    }
else
    echo "⚠️ PostgreSQL binaries not found. Ensure pg_ctl/initdb are available in replit.nix"
    exit 1
fi

# Setup database
echo "🗄️ Setting up database..."
node scripts/setup-database.js

# Check if Redis is available (optional)
if command -v redis-server &> /dev/null; then
    echo "🔄 Starting Redis..."
    redis-server --daemonize yes 2>/dev/null || true
else
    echo "ℹ️ Redis not available, using memory cache"
fi

# Build the application if needed
if [ ! -d "dist" ] && [ "$NODE_ENV" == "production" ]; then
    echo "🔨 Building application for production..."
    pnpm build
fi

# Start services
echo ""
echo "🎯 Starting Voice by Kraliki services..."
echo "================================"

if [ -n "$REPL_SLUG" ] && [ -n "$REPL_OWNER" ]; then
    echo "📍 Frontend: https://$REPL_SLUG.$REPL_OWNER.repl.co"
    echo "📍 Backend API: https://$REPL_SLUG.$REPL_OWNER.repl.co/api"
    echo "📍 tRPC Panel: https://$REPL_SLUG.$REPL_OWNER.repl.co/trpc-panel"
else
    echo "📍 Frontend: http://localhost:3007"
    echo "📍 Backend API: http://localhost:3010"
    echo "📍 tRPC Panel: http://localhost:3010/trpc-panel"
fi

echo "================================"
echo ""
echo "📚 Default credentials:"
echo "   Admin: admin@cc-light.local / Admin123!@#"
echo "   Supervisor: supervisor@cc-light.local / Supervisor123!@#"
echo "   Agent: agent1@cc-light.local / Agent123!@#"
echo ""

# Use concurrently to run both services
exec pnpm dev:all
