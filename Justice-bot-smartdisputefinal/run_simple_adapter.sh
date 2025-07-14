#!/bin/bash
# Script to run the simple port adapter for SmartDispute.ai

echo "===== Starting SmartDispute.ai Simple Port Adapter ====="
echo "This script forwards requests from port 8080 to port 5000"
echo ""

# Make the script executable
chmod +x simple_port_adapter.py

# Clean up any existing port adapters
echo "Cleaning up any running port adapters..."
pkill -f "python simple_port_adapter.py" || true

# Start the port adapter in the background
echo "Starting simple port adapter..."
nohup python simple_port_adapter.py > simple_adapter.log 2>&1 &
ADAPTER_PID=$!
echo "Port adapter started with PID: $ADAPTER_PID"
echo $ADAPTER_PID > simple_adapter.pid

echo ""
echo "Simple port adapter is now running in the background."
echo "Port 8080 should now be forwarding to port 5000."
echo "You can monitor it with: cat simple_adapter.log"
echo ""

# Test the connectivity after a short delay
sleep 2
echo "Testing connectivity:"
curl -s http://localhost:8080/health || echo "Failed to connect to port 8080"