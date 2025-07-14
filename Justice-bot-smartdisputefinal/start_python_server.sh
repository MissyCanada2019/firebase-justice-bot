#!/bin/bash

# This script starts both the main application on port 5000
# and the Python HTTP server on port 8080

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes
pkill -f "gunicorn" || true
pkill -f "python.*python_server.py" || true

# Start the main application on port 5000
echo "Starting main application on port 5000..."
gunicorn main:app --bind 0.0.0.0:5000 --workers 2 --daemon

# Wait a moment for the main application to start
sleep 2

# Start the Python HTTP server on port 8080
echo "Starting Python HTTP server on port 8080..."
python python_server.py
