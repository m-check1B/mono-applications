#!/bin/bash
# Focus by Kraliki - Database Reset
# Resets the database (DANGER: Deletes all data!)

set -e

echo "⚠️  Focus by Kraliki - Database Reset"
echo "=============================="
echo ""
echo "This will DELETE ALL DATA from the database!"
read -p "Are you sure? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

cd backend
source venv/bin/activate

echo "Dropping all tables..."
alembic downgrade base

echo "Running migrations..."
alembic upgrade head

echo ""
echo "✅ Database reset complete!"
echo ""
echo "Optional: Seed database with sample data"
echo "  python -m app.seed  # (if seed script exists)"
