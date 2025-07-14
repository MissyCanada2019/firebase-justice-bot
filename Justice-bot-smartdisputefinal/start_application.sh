#!/bin/bash

# Combined startup script for SmartDispute.ai
# This script starts both the main application on port 5000
# and the port forwarder to provide port 8080 access required by Replit

echo "Starting SmartDispute.ai..."

# 1. First, kill any existing processes
echo "Stopping any existing servers..."
pkill -f "gunicorn" || true
pkill -f "python.*port_forwarder.py" || true

# 2. Create log directory if it doesn't exist
mkdir -p logs

# 3. Start the main application with gunicorn on port 5000
echo "Starting main application on port 5000..."
gunicorn --bind 0.0.0.0:5000 --workers 1 --reload main:app > logs/main_app.log 2>&1 &
MAIN_PID=$!
echo $MAIN_PID > main_app.pid
echo "Main app started with PID $MAIN_PID"

# 4. Wait for the main app to initialize (5 seconds)
echo "Waiting for main application to initialize..."
sleep 5

# 5. Start the port forwarder on port 8080
echo "Starting port forwarder on port 8080..."
python port_forwarder.py > logs/port_forwarder.log 2>&1 &
FORWARDER_PID=$!
echo $FORWARDER_PID > port_forwarder.pid
echo "Port forwarder started with PID $FORWARDER_PID"

# 6. Create a combined PID file for easy monitoring
echo "$MAIN_PID $FORWARDER_PID" > combined.pid

# 7. Show status information
echo ""
echo "=== SmartDispute.ai is now running ==="
echo "Main application: http://localhost:5000 (PID: $MAIN_PID)"
echo "Web interface: http://localhost:8080 (PID: $FORWARDER_PID)"
echo "Log files:"
echo "  - Main application: logs/main_app.log"
echo "  - Port forwarder: logs/port_forwarder.log"
echo ""
echo "Use ./stop_application.sh to stop all services"
