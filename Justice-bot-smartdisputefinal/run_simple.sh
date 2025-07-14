#!/bin/bash
# Script to run the simple HTTP server for port forwarding

echo "======================================================"
echo "     Running SmartDispute.ai Port Forwarding"
echo "======================================================"
echo "This script starts a lightweight HTTP server that forwards requests from port 8080 to port 5000"
echo ""

# Kill any existing processes to avoid port conflicts
echo "Cleaning up existing processes..."
pkill -f "python.*simple_http_server.py" || true

# Start the simple HTTP server forwarder
echo "Starting simple HTTP server forwarder..."
chmod +x simple_http_server.py
python simple_http_server.py -v