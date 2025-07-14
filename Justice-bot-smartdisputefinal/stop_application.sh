#!/bin/bash

# Stop script for SmartDispute.ai
# This script stops both the main application and the port forwarder

echo "Stopping SmartDispute.ai..."

# 1. Read PIDs from files if they exist
if [ -f "main_app.pid" ]; then
    MAIN_PID=$(cat main_app.pid)
    echo "Stopping main application (PID: $MAIN_PID)..."
    kill $MAIN_PID 2>/dev/null || true
    rm main_app.pid
fi

if [ -f "port_forwarder.pid" ]; then
    FORWARDER_PID=$(cat port_forwarder.pid)
    echo "Stopping port forwarder (PID: $FORWARDER_PID)..."
    kill $FORWARDER_PID 2>/dev/null || true
    rm port_forwarder.pid
fi

# 2. Cleanup combined PID file
if [ -f "combined.pid" ]; then
    rm combined.pid
fi

# 3. Kill any remaining processes (in case PID files are out of sync)
echo "Ensuring all processes are stopped..."
pkill -f "gunicorn" || true
pkill -f "python.*port_forwarder.py" || true

echo "All services stopped successfully"
