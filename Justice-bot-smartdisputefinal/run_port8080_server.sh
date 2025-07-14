#!/bin/bash
# Start the port 8080 server

echo "======================================"
echo "    SmartDispute.ai Port 8080 Server   "
echo "======================================"
echo "This script runs a Flask app on port 8080 to redirect to the main app"

# Clean up any existing servers
echo "Cleaning up existing servers..."
pkill -f "python.*port8080.py" || true

# Start the server in the background
echo "Starting port 8080 server..."
python port8080.py > port8080_server.log 2>&1 &

# Save PID
PORT8080_PID=$!
echo "Port 8080 server started with PID: $PORT8080_PID"
echo $PORT8080_PID > port8080_server.pid

echo ""
echo "Port 8080 server is running!"
echo "Server log: port8080_server.log"
echo "======================================"
