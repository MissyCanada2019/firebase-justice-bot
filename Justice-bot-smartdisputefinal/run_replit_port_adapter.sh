#!/bin/bash
# Run the Replit Port Adapter for SmartDispute.ai

echo "===================================================="
echo "       SmartDispute.ai Replit Port Adapter"
echo "===================================================="
echo "This script sets up port 8080 forwarding for Replit"
echo ""

# Kill any existing port adapters/forwarders
echo "Cleaning up existing processes..."

# Stop previous instances of this adapter
if [ -f replit_port_adapter.pid ]; then
    echo "Stopping existing port adapter..."
    PID=$(cat replit_port_adapter.pid)
    kill -15 $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
    rm -f replit_port_adapter.pid
fi

# Kill any other port forwarders that might be running
pkill -f "python.*port_forwarder.py" || true
pkill -f "python.*simple_port_forward.py" || true
pkill -f "python.*auto_port_forward.py" || true
pkill -f "python.*port8080.py" || true
pkill -f "python.*minimal_redirect.py" || true

# Make the script executable
chmod +x replit_port_adapter.py

# Start the Replit port adapter
echo "Starting Replit port adapter..."
python replit_port_adapter.py &
ADAPTER_PID=$!
echo "Replit port adapter started with PID: $ADAPTER_PID"

echo ""
echo "Replit port adapter is now running!"
echo "Port 8080 is being forwarded to the main application on port 5000"
echo "===================================================="