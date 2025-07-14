#!/bin/bash
# Direct script to run the port adapter for SmartDispute.ai

echo "==== SmartDispute.ai Port Adapter (Port 8080) ===="
echo "Starting port adapter on port 8080..."

# Kill any existing port adapter processes
pkill -f "python port_adapter_workflow.py" || true

# Wait for a moment
sleep 1

# Try to start the port adapter with Flask directly
nohup python port_adapter_workflow.py > port_adapter.log 2>&1 &

# Store the PID
PORT_ADAPTER_PID=$!
echo "Port adapter started with PID: $PORT_ADAPTER_PID"
echo $PORT_ADAPTER_PID > port_adapter.pid

echo "Port adapter started successfully!"
echo "Access via port 8080 should now be available."