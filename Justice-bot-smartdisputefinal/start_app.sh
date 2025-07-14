#!/bin/bash
# This script starts both the main application and the port 8080 adapter

echo "===== SmartDispute.ai Startup Script ====="
echo "Starting both main application and port 8080 adapter..."

# Kill any existing port adapter
pkill -f "python port8080.py" || true

# Start the port adapter in the background
echo "Starting port 8080 adapter..."
nohup python port8080.py > port8080.log 2>&1 &
ADAPTER_PID=$!
echo "Port adapter started with PID: $ADAPTER_PID"
echo $ADAPTER_PID > port8080.pid

# Start main application
echo "Starting main application on port 5000..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app