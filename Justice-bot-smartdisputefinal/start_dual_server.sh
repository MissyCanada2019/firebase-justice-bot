#!/bin/bash

# Start script for the dual server (5000 + 8080)

echo "Starting SmartDispute.ai dual server..."

# Kill any existing processes
pkill -f "python.*dual_server.py" || true
pkill -f "gunicorn" || true
pkill -f "python.*simplified_8080.py" || true

# Start the dual server
python dual_server.py &
DUAL_PID=$!
echo $DUAL_PID > dual_server.pid

echo "Dual server started with PID $DUAL_PID"
echo "Servers available at:"
echo "  - Main app: http://localhost:5000/"
echo "  - Port 8080: http://localhost:8080/"
