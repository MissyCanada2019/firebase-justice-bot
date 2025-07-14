#!/bin/bash
# Start both the main application and the port 8080 adapter

# Kill any existing processes
echo "Cleaning up any existing processes..."
pkill -f "python.*port8080.py" || true
pkill -f "python.*replit_port_8080.py" || true
pkill -f "python.*port_adapter.py" || true
pkill -f "python.*simple_port_forward.py" || true
pkill -f "python.*minimal_port_forward.py" || true

# Start the port 8080 adapter in the background
echo "Starting port 8080 adapter..."
python port8080.py &
PORT_ADAPTER_PID=$!

# Save the PID for later cleanup
echo $PORT_ADAPTER_PID > port_adapter.pid

# Log the startup
echo "Port 8080 adapter started with PID: $PORT_ADAPTER_PID"
echo "SmartDispute.ai should be accessible on both port 5000 and 8080"

# Create a cleanup function
cleanup() {
    echo "Cleaning up processes..."
    if [ -f port_adapter.pid ]; then
        PORT_PID=$(cat port_adapter.pid)
        kill $PORT_PID 2>/dev/null || true
        rm port_adapter.pid
    fi
    pkill -f "python.*port8080.py" || true
    exit 0
}

# Register the cleanup function for signals
trap cleanup SIGINT SIGTERM EXIT

# Wait for the port adapter to finish (which should be never unless it crashes)
wait $PORT_ADAPTER_PID
