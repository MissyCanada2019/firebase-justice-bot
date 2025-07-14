#!/bin/bash
# Run the simple HTTP server on port 8080

echo "======================================"
echo "    SmartDispute.ai HTTP Server     "
echo "======================================"
echo "This script runs a simple HTTP server on port 8080 that forwards to port 5000"

# Clean up any existing HTTP servers
echo "Cleaning up existing servers..."
pkill -f "python.*simple_http_server.py" || true

# Start HTTP server in the background
echo "Starting HTTP server on port 8080..."
python simple_http_server.py > http_server.log 2>&1 &

# Save PID to use later if we need to stop the server
HTTP_PID=$!
echo "HTTP server started with PID: $HTTP_PID"
echo $HTTP_PID > http_server.pid

echo ""
echo "HTTP server is running and forwarding requests from port 8080 to port 5000!"
echo "Server log: http_server.log"
echo "======================================"
