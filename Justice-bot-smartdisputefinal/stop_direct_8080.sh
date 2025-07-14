#!/bin/bash

# Stop script for direct 8080 server
# This script stops the direct Flask application running on port 8080

echo "Stopping direct 8080 server..."

# 1. Read PID from file if it exists
if [ -f "direct_8080.pid" ]; then
    SERVER_PID=$(cat direct_8080.pid)
    echo "Stopping server (PID: $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null || true
    rm direct_8080.pid
fi

# 2. Kill any remaining processes (in case PID file is out of sync)
echo "Ensuring all processes are stopped..."
pkill -f "python.*direct_8080_server.py" || true

echo "Server stopped successfully"
