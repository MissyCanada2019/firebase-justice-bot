#!/bin/bash
# Direct port 8080 server script for SmartDispute.ai
# This script runs the application directly on port 8080 only

# Kill any existing gunicorn processes
echo "Stopping any existing gunicorn processes..."
pkill -9 -f gunicorn || true
sleep 2

# Set environment variables
export PORT=8080

# Start the application on port 8080
echo "Starting SmartDispute.ai on port 8080..."
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 main:app