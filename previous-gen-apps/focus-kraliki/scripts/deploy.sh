#!/bin/bash
# Focus by Kraliki Deployment Script (FastAPI + SvelteKit)
# Deploys backend (FastAPI) and frontend (SvelteKit) with PM2 supervision

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check environment
if [ "$1" != "production" ]; then
    print_error "Usage: ./deploy.sh production"
    exit 1
fi

print_info "Starting Focus by Kraliki production deployment..."

# Navigate to project root (scripts/..)
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Pull latest code
print_status "Pulling latest code from git..."
git pull origin main

# Backend deployment
print_status "Deploying FastAPI backend..."
cd backend

# Create virtualenv if missing
if [ ! -d ".venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

print_info "Installing Python dependencies..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

print_info "Applying database migrations (Alembic)..."
alembic upgrade head

deactivate
cd "$ROOT_DIR"

# Frontend deployment
print_status "Building SvelteKit frontend..."
cd frontend
pnpm install --frozen-lockfile
pnpm build
cd "$ROOT_DIR"

# Stop existing PM2 processes
print_status "Restarting PM2 processes..."
pm2 stop focus-kraliki-backend 2>/dev/null || true
pm2 stop focus-kraliki-frontend 2>/dev/null || true
pm2 delete focus-kraliki-backend 2>/dev/null || true
pm2 delete focus-kraliki-frontend 2>/dev/null || true

# Start backend via uvicorn inside the virtualenv
pm2 start "$ROOT_DIR/backend/.venv/bin/uvicorn" \\
    --name focus-kraliki-backend \\
    --cwd "$ROOT_DIR/backend" \\
    --interpreter none \\
    -- "app.main:app" --host 127.0.0.1 --port 3017

# Serve the built frontend via Vite preview (change port as needed)
pm2 start pnpm \\
    --name focus-kraliki-frontend \\
    --cwd "$ROOT_DIR/frontend" \\
    -- run preview -- --host 127.0.0.1 --port 5175

pm2 save

# Health check
print_status "Performing health check..."
sleep 5

# Check backend health
if curl -f http://127.0.0.1:3017/health > /dev/null 2>&1; then
    print_status "Backend health check passed"
else
    print_error "Backend health check failed"
    pm2 logs focus-kraliki-backend --lines 50
    exit 1
fi

# Check frontend health
if curl -f http://127.0.0.1:5175 > /dev/null 2>&1; then
    print_status "Frontend health check passed"
else
    print_error "Frontend health check failed"
    pm2 logs focus-kraliki-frontend --lines 50
    exit 1
fi

# Show status
print_status "Deployment complete!"
print_info "Application status:"
pm2 status

echo ""
print_info "Access URLs:"
echo "  Frontend: http://127.0.0.1:5175"
echo "  API: http://127.0.0.1:3017"
echo ""
print_info "View logs with:"
echo "  pm2 logs focus-kraliki-backend"
echo "  pm2 logs focus-kraliki-frontend"
echo ""
print_info "Monitor with:"
echo "  pm2 monit"
