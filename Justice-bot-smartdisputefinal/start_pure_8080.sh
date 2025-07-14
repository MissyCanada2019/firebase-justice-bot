#!/bin/bash

# Start pure Python HTTP server on port 8080
# This script uses a pure Python implementation with no dependencies

echo "Starting pure Python HTTP server on port 8080..."

# Kill any existing instances
pkill -f "python.*pure_8080.py" || true

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the server
python pure_8080.py > logs/pure_8080.log 2>&1 &
PURE_PID=$!
echo $PURE_PID > pure_8080.pid

echo "Pure Python server started with PID $PURE_PID"
echo "Log file: logs/pure_8080.log"
