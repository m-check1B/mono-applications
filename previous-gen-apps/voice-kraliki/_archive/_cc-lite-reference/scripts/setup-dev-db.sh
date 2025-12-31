#!/usr/bin/env bash
set -euo pipefail
echo "🔧 Starting local dev DB services (Docker) and migrating..."
if command -v docker >/dev/null 2>&1; then
  docker compose -f docker-compose.dev.yml up -d
else
  echo "⚠️ Docker not found, skipping containers."
fi
node scripts/setup-database.js
echo "✅ Dev DB ready."

