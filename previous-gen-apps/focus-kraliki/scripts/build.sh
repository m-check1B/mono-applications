#!/bin/bash
# Focus by Kraliki - Production Build
# Builds both backend and frontend for production deployment

set -e

echo "🏗️  Focus by Kraliki - Production Build"
echo "================================="
echo ""

# Build frontend
echo "Building frontend..."
cd frontend
pnpm build
echo "✅ Frontend build complete (frontend/build/)"
cd ..

# Backend doesn't need building (Python), but we can prepare it
echo ""
echo "Preparing backend..."
cd backend
source venv/bin/activate
pip install -r requirements.txt --quiet
echo "✅ Backend dependencies installed"
cd ..

echo ""
echo "✅ Production build complete!"
echo ""
echo "Deployment files:"
echo "  Frontend: frontend/build/"
echo "  Backend: backend/ (with venv/)"
echo ""
echo "Next steps:"
echo "1. Deploy frontend build to Vercel/Netlify/Cloudflare Pages"
echo "2. Deploy backend to Railway/Render/Fly.io"
echo "3. Set up production database (PostgreSQL)"
echo "4. Configure environment variables on hosting platforms"
