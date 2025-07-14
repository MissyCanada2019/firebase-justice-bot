#!/bin/bash
# Script to run the SmartDispute.ai application on port 8080

echo "======================================================"
echo "     Running SmartDispute.ai on Port 8080 DIRECTLY    "
echo "======================================================"
echo "IMPORTANT: This will start the application on port 8080 directly"
echo "rather than port 5000 to ensure reliable accessibility."
echo ""

# Kill any existing processes to avoid port conflicts
echo "Cleaning up existing processes..."
pkill -f "gunicorn.*main:app" || true
pkill -f "python.*main_8080.py" || true
pkill -f "gunicorn.*port8080:app" || true
pkill -f "python.*simple_http_server.py" || true

# Start the application with gunicorn on port 8080
echo "Starting SmartDispute.ai on port 8080..."
gunicorn --bind 0.0.0.0:8080 --reuse-port --reload main:app