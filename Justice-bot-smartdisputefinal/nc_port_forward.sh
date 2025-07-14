#!/bin/bash
# Simple port forwarding using netcat
# Forwards port 8080 to port 5000

echo "Starting port forwarder: 8080 -> 5000"

# Kill any existing nc processes
pkill -f "nc.*8080" || true

while true; do
    nc -l -p 8080 -c "nc localhost 5000" > /dev/null 2>&1
    echo "Restarting netcat forwarder..."
    sleep 1
done
