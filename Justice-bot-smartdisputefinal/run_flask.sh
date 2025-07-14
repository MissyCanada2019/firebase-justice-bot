#!/bin/bash
# Main entry script for SmartDispute.ai that starts both server components
# - Main application on port 5000
# - Port 8080 adapter for Replit proxy access

echo "===== SmartDispute.ai Startup Script ====="
echo "Version: 1.0.0"
echo "Date: April 28, 2025"
echo ""

# Kill any existing port adapter
echo "Cleaning up any running port adapters..."
pkill -f "python port8080.py" || true

# Start the port adapter in the background
echo "Starting port 8080 adapter..."
nohup python port8080.py > port8080.log 2>&1 &
ADAPTER_PID=$!
echo "Port adapter started with PID: $ADAPTER_PID"
echo $ADAPTER_PID > port8080.pid

# Give the port adapter a moment to start
sleep 1

# Display a welcome message
echo ""
echo "=========================================="
echo "SmartDispute.ai is starting up!"
echo "The application will be accessible through both:"
echo "- Port 5000 (Main application)"
echo "- Port 8080 (Port adapter)"
echo ""
echo "You can monitor the port adapter with:"
echo "  cat port8080.log"
echo "=========================================="
echo ""

# Start main application
echo "Starting main application on port 5000..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app