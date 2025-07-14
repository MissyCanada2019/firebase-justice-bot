#!/bin/bash
# Run SmartDispute.ai with port forwarding

echo "====================================================="
echo "    SmartDispute.ai with Port Forwarding"
echo "====================================================="
echo "This script runs the main application on port 5000 and forwards port 8080 to it"
echo ""

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f "python.*simple_port_forward.py" || true

# Make sure the port forwarding script is executable
chmod +x simple_port_forward.py

# Start the port 8080 forwarder in the background
echo "Starting port 8080 forwarder..."
python simple_port_forward.py > port_forward.log 2>&1 &
FORWARDER_PID=$!
echo "Port forwarder started with PID: $FORWARDER_PID"
echo $FORWARDER_PID > port_forwarder.pid

echo ""
echo "Port forwarding is active from 8080 to 5000!"
echo "Port forwarder log: port_forward.log"
echo "====================================================="