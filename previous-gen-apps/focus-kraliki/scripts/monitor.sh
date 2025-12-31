#!/bin/bash

# Focus by Kraliki Monitoring Script
# Checks health of all services

set -e

# Detect compose file
COMPOSE_FILE="docker-compose.yml"
if [ -f "docker-compose.prod.yml" ] && docker compose -f docker-compose.prod.yml ps -q &>/dev/null; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo "🔍 Focus by Kraliki Health Check"
echo "=========================="
echo "📝 Using compose file: $COMPOSE_FILE"
echo ""

# Check if services are running
echo "📊 Service Status:"
docker compose -f "$COMPOSE_FILE" ps
echo ""

# Check backend health
echo "🏥 Backend Health:"
if curl -sf http://127.0.0.1:3017/health > /dev/null; then
    BACKEND_RESPONSE=$(curl -s http://127.0.0.1:3017/health)
    echo "✅ Backend is healthy"
    echo "   Response: $BACKEND_RESPONSE"
else
    echo "❌ Backend is not responding"
fi
echo ""

# Check frontend
echo "🏥 Frontend Health:"
if curl -sf http://127.0.0.1:5175 > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not responding"
fi
echo ""

# Check database
echo "🗄️  Database Health:"
if docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is ready"

    # Get database size
    DB_SIZE=$(docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U postgres -d focus_kraliki -t -c "SELECT pg_size_pretty(pg_database_size('focus_kraliki'));" | tr -d ' ')
    echo "   Size: $DB_SIZE"
else
    echo "❌ Database is not ready"
fi
echo ""

# Check Redis
echo "💾 Redis Health:"
if docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is responding"

    # Get memory usage
    REDIS_MEMORY=$(docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli INFO memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    echo "   Memory: $REDIS_MEMORY"
else
    echo "❌ Redis is not responding"
fi
echo ""

# Check disk usage
echo "💽 Disk Usage:"
df -h | grep -E "Filesystem|/dev/" || df -h
echo ""

# Check Docker resource usage
echo "🐳 Docker Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker compose -f "$COMPOSE_FILE" ps -q)
echo ""

# Check recent errors in logs
echo "⚠️  Recent Errors (last 10):"
docker compose -f "$COMPOSE_FILE" logs --tail=100 2>&1 | grep -i "error\|exception\|fatal" | tail -10 || echo "   No recent errors found"
echo ""

echo "✅ Health check complete!"
