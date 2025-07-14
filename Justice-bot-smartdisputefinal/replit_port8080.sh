#!/bin/bash
# Script to run the port 8080 server for SmartDispute.ai
# This handles redirecting port 8080 to the main application on port 5000

set -e

echo "Starting port 8080 server..."

# Kill any existing server processes
pkill -f "python.*simple_port8080.py" || true

# Start the server
python3 simple_port8080.py &

# Save the PID
echo $! > port8080.pid

echo "Port 8080 server started with PID $(cat port8080.pid)"