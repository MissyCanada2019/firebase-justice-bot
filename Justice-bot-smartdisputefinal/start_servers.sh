#!/bin/bash

# Start servers script for SmartDispute.ai
# This script starts both the main app on port 5000 and a port 8080 forwarder

echo "Starting both servers..."

# Kill any existing processes
pkill -f "gunicorn --bind 0.0.0.0:5000" || true
pkill -f "python simple_port8080.py" || true

# Start the main application on port 5000 (background)
echo "Starting main application on port 5000..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app > gunicorn.log 2>&1 &

# Wait for the main app to start
echo "Waiting for main app to initialize..."
sleep 5

# Start the port 8080 forwarder (background)
echo "Starting port 8080 forwarder..."
python simple_port8080.py > port8080.log 2>&1 &

echo "Both servers started in background mode."
echo "Main app: port 5000"
echo "Forwarder: port 8080"
