#!/bin/bash

# Focus by Kraliki Development Setup Script
# This script sets up the development environment without Docker

echo "🚀 Setting up Focus by Kraliki Development Environment"
echo "=================================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL:"
    echo "   brew install postgresql"
    echo "   brew services start postgresql"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js:"
    echo "   brew install node"
    exit 1
fi

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm is not installed. Installing..."
    npm install -g pnpm
fi

echo "✅ Prerequisites checked"

# Create database if it doesn't exist
echo "📊 Setting up PostgreSQL database..."
createdb focus_kraliki 2>/dev/null || echo "Database already exists"

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "🔧 Creating environment configuration..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env - please update with your API keys"
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pnpm install

# Generate Prisma client
echo "🗄️ Generating Prisma client..."
pnpm prisma generate

# Run database migrations
echo "🔄 Running database migrations..."
pnpm prisma migrate dev --name init

# Seed database with sample data
echo "🌱 Seeding database with sample data..."
psql -d focus_kraliki -f ../init.sql 2>/dev/null || echo "Sample data already exists or will be added later"

cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
pnpm install

cd ..

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit backend/.env with your API keys:"
echo "   - ANTHROPIC_API_KEY"
echo "   - OPENROUTER_API_KEY or OPENAI_API_KEY"
echo "   - DEEPGRAM_API_KEY"
echo ""
echo "2. Start the development servers:"
echo "   Terminal 1: cd backend && pnpm dev"
echo "   Terminal 2: cd frontend && pnpm dev"
echo ""
echo "3. Open http://127.0.0.1:5175 in your browser"
echo ""
echo "🔧 Database Management:"
echo "   View database: cd backend && pnpm prisma studio"
echo "   Reset database: cd backend && pnpm prisma migrate reset"
echo ""
echo "🚀 Happy coding!"