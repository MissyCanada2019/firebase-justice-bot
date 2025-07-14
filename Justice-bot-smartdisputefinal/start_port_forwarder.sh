#!/bin/bash
# Script to start the port 8080 adapter in the background

echo "===== SmartDispute.ai Port 8080 Adapter ====="
echo "Starting port 8080 adapter in the background..."

# Kill any existing port adapter
echo "Cleaning up any running port adapters..."
pkill -f "python port8080.py" || true

# Start the port adapter in the background
echo "Starting port 8080 adapter..."
nohup python port8080.py > port8080.log 2>&1 &
ADAPTER_PID=$!
echo "Port adapter started with PID: $ADAPTER_PID"
echo $ADAPTER_PID > port8080.pid

echo ""
echo "Port 8080 adapter is now running in the background."
echo "You can monitor it with: cat port8080.log"
echo "To stop it later, run: kill \$(cat port8080.pid)"
echo ""