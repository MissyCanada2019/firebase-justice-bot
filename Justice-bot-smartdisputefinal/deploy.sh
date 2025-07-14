#!/bin/bash

# SmartDispute.ai Deployment Script
# This script runs the main application on port 5000
# and a redirecting server on port 8080 for Replit compatibility

echo "Starting SmartDispute.ai deployment..."

# Ensure dependencies are installed
echo "Ensuring dependencies are installed..."
pip install -r requirements.txt > /dev/null 2>&1

# Kill any existing processes
echo "Stopping any existing servers..."
pkill -f "gunicorn" > /dev/null 2>&1
pkill -f "python simple_redirect.py" > /dev/null 2>&1

# Start the main application with gunicorn on port 5000
echo "Starting main application on port 5000..."
nohup gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app > gunicorn.log 2>&1 &
MAIN_PID=$!
echo $MAIN_PID > main_app.pid
echo "Main application started with PID: $MAIN_PID"

# Wait for the main app to initialize
sleep 3

# Start the redirect server on port 8080
echo "Starting redirect server on port 8080..."
chmod +x simple_redirect.py
nohup python simple_redirect.py > redirect.log 2>&1 &
REDIRECT_PID=$!
echo $REDIRECT_PID > redirect.pid
echo "Redirect server started with PID: $REDIRECT_PID"

echo ""
echo "SmartDispute.ai is now running!"
echo "Main application: http://localhost:5000 (PID: $MAIN_PID)"
echo "Redirect server: http://localhost:8080 (PID: $REDIRECT_PID)"
echo "Logs available in gunicorn.log and redirect.log"
echo ""
echo "Use './stop.sh' to stop all servers"
