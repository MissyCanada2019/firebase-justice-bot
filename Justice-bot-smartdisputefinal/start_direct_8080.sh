#!/bin/bash

# Direct port 8080 startup script for SmartDispute.ai
# This script starts a direct Flask application on port 8080

echo "Starting SmartDispute.ai directly on port 8080..."

# 1. Stop any existing servers
echo "Stopping any existing servers..."
pkill -f "python.*direct_8080_server.py" || true

# 2. Create log directory if needed
mkdir -p logs

# 3. Start the server
echo "Starting server on port 8080..."
python direct_8080_server.py > logs/direct_8080.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > direct_8080.pid

echo "Direct server started with PID $SERVER_PID"
echo "Log file: logs/direct_8080.log"
