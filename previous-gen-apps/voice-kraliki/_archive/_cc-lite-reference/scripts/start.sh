#!/usr/bin/env bash
set -euo pipefail
export NODE_ENV=${NODE_ENV:-production}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-3010}
export FRONTEND_PORT=${FRONTEND_PORT:-3007}

echo "Starting Voice by Kraliki (server: $HOST:$PORT, frontend: $HOST:$FRONTEND_PORT)"

# Start both preview (serves dist) and server
exec pnpm start:all

