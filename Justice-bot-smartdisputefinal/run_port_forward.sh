#!/bin/bash
# Script to run the SmartDispute.ai TCP port forwarder

echo "===== Starting SmartDispute.ai TCP Port Forwarder ====="
echo "This script forwards connections from port 8080 to port 5000"
echo ""

# Make the script executable
chmod +x tcp_port_forward.py

# Kill any existing port forwarder processes
echo "Cleaning up any running port forwarders..."
pkill -f "python tcp_port_forward.py" || true
pkill -f "python port8080.py" || true

# Wait a moment for processes to terminate
sleep 1

# Start the TCP port forwarder in the background
echo "Starting TCP port forwarder..."
nohup python tcp_port_forward.py > tcp_port_forward.log 2>&1 &
FORWARDER_PID=$!
echo "Port forwarder started with PID: $FORWARDER_PID"
echo $FORWARDER_PID > tcp_port_forward.pid

echo ""
echo "TCP port forwarder is now running in the background."
echo "Port 8080 should now be forwarding to port 5000."
echo "You can monitor it with: cat tcp_port_forward.log"
echo "To stop it later, run: kill \$(cat tcp_port_forward.pid)"
echo ""