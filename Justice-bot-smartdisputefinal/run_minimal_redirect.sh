#!/bin/bash
# Run SmartDispute.ai minimal redirect server

echo "====================================================="
echo "    SmartDispute.ai Minimal Port Redirector"
echo "====================================================="
echo "This script runs a minimal HTTP server on port 8080 that forwards to port 5000"
echo ""

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f "python.*minimal_redirect.py" || true

# Make sure the script is executable
chmod +x minimal_redirect.py

# Start the minimal redirector in the background
echo "Starting minimal redirector..."
python minimal_redirect.py > minimal_redirect.log 2>&1 &
REDIRECTOR_PID=$!
echo "Minimal redirector started with PID: $REDIRECTOR_PID"
echo $REDIRECTOR_PID > minimal_redirect.pid

echo ""
echo "Port 8080 forwarding is active!"
echo "Forwarding requests from port 8080 to port 5000"
echo "Redirector log: minimal_redirect.log"
echo "====================================================="