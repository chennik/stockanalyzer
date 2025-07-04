#!/bin/bash

# Stock Analyzer Server Startup Script

echo "🚀 Starting Stock Analyzer Server..."

# Check if server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Server is already running on port 8000"
    echo "   Run ./stop_server.sh to stop it first"
    exit 1
fi

# Clean up any stale processes
pkill -f "python.*ui/server.py" 2>/dev/null

# Wait a moment for cleanup
sleep 1

# Start the server in the background
nohup python3 ui/server.py > server.log 2>&1 &
SERVER_PID=$!

# Save PID to file for stop script
echo $SERVER_PID > .server.pid

# Wait and check if server started successfully
sleep 2

if ps -p $SERVER_PID > /dev/null ; then
    echo "✅ Server started successfully!"
    echo "   PID: $SERVER_PID"
    echo "   URL: http://localhost:8000"
    echo "   Logs: tail -f server.log"
    echo ""
    echo "To stop the server, run: ./stop_server.sh"
else
    echo "❌ Failed to start server"
    echo "   Check server.log for errors"
    exit 1
fi