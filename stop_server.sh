#!/bin/bash

# Stock Analyzer Server Shutdown Script

echo "🛑 Stopping Stock Analyzer Server..."

# Method 1: Try using saved PID first
if [ -f .server.pid ]; then
    SERVER_PID=$(cat .server.pid)
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo "   Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null
        
        # Wait for graceful shutdown
        sleep 2
        
        # Force kill if still running
        if ps -p $SERVER_PID > /dev/null 2>&1; then
            echo "   Force stopping server..."
            kill -9 $SERVER_PID 2>/dev/null
        fi
        
        rm -f .server.pid
        echo "✅ Server stopped successfully"
    else
        echo "⚠️  Server PID $SERVER_PID not found"
        rm -f .server.pid
    fi
fi

# Method 2: Kill any remaining Python server processes
REMAINING=$(pgrep -f "python.*ui/server.py")
if [ ! -z "$REMAINING" ]; then
    echo "   Cleaning up remaining processes..."
    pkill -f "python.*ui/server.py"
    sleep 1
fi

# Method 3: Ensure port 8000 is free
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "   Freeing up port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
fi

# Verify server is stopped
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Server stopped and port 8000 is free"
else
    echo "❌ Warning: Port 8000 might still be in use"
fi