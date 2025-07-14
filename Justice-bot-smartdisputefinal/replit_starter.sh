#!/bin/bash
# Script to start the Flask server optimized for Replit

echo "===== SmartDispute.ai Replit Starter ====="
echo "Starting server on port 5000..."
echo "This version is optimized for Replit deployment"
echo ""

# Kill any existing processes
echo "Checking for existing processes..."
pkill -f gunicorn || true

# Start with gunicorn using the Replit-optimized main file
echo "Starting server with gunicorn..."
gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 replit_main:app