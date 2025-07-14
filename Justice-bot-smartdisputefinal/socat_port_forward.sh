#!/bin/bash
# Port forwarding using socat
# Forwards port 8080 to port 5000

echo "Starting socat port forwarder: 8080 -> 5000"

# Kill any existing socat processes
pkill -f "socat.*8080" || true

# Start socat in the background
socat TCP4-LISTEN:8080,fork TCP4:localhost:5000 &

# Save PID
SOCAT_PID=$!
echo "Port forwarder started with PID: $SOCAT_PID"
echo $SOCAT_PID > socat_port_forward.pid

echo "Port forwarder is running!"
