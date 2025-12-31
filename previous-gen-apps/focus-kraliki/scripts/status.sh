#!/bin/bash

# Focus by Kraliki Development Server Status
# Shows the current status of the development servers

echo "🚀 Focus by Kraliki Development Servers"
echo "=================================="
echo ""

# Check Backend Server
BACKEND_PID=$(lsof -ti:3018 2>/dev/null)
if [ ! -z "$BACKEND_PID" ]; then
    echo "✅ Backend Server: RUNNING"
    echo "   URL: http://127.0.0.1:3018"
    echo "   Health: http://127.0.0.1:3018/health"
    echo "   PID: $BACKEND_PID"
    echo ""
    
    # Test backend endpoint
    HEALTH_RESPONSE=$(curl -s http://127.0.0.1:3018/health 2>/dev/null)
    if [ ! -z "$HEALTH_RESPONSE" ]; then
        echo "   Status: $(echo $HEALTH_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
        echo "   Version: $(echo $HEALTH_RESPONSE | grep -o '"version":"[^"]*"' | cut -d'"' -f4)"
    fi
else
    echo "❌ Backend Server: STOPPED"
fi

echo ""

# Check Frontend Server
FRONTEND_PID=$(lsof -ti:5173 2>/dev/null)
if [ ! -z "$FRONTEND_PID" ]; then
    echo "✅ Frontend Server: RUNNING"
    echo "   URL: http://localhost:5173"
    echo "   PID: $FRONTEND_PID"
    echo ""
    
    # Test frontend accessibility
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   Status: Accessible (HTTP $HTTP_CODE)"
    else
        echo "   Status: Not accessible (HTTP $HTTP_CODE)"
    fi
else
    echo "❌ Frontend Server: STOPPED"
fi

echo ""
echo "📝 How to use:"
echo "1. Open your browser and go to: http://localhost:5173"
echo "2. The app will load with mock data for demonstration"
echo "3. You can test all features including AI chat, task management, etc."
echo "4. Backend API is available at: http://127.0.0.1:3018/api"
echo ""

echo "🔧 Available Features:"
echo "- User Registration/Login (Mock)"
echo "- Task CRUD Operations"
echo "- AI Chat Interface (Demo responses)"
echo "- Task Generation from Natural Language"
echo "- User Preferences"
echo "- Theme Switching"
echo ""

echo "🛑 To stop the servers:"
echo "   pkill -f 'tsx.*dev-server'"
echo "   pkill -f 'vite.*dev'"