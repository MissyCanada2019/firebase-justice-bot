#!/bin/bash
# Script to start the simplified server for Replit

echo "===== SmartDispute.ai Quick Server ====="
echo "Starting simplified server on port 5000..."

# Clean up any previous server processes
echo "Checking for existing processes..."
pkill -f gunicorn || true
sleep 1

# Start the server with gunicorn
echo "Starting server with gunicorn..."
gunicorn --workers 1 --bind 0.0.0.0:5000 quick_server:app