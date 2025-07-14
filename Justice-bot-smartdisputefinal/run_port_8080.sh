#!/bin/bash
# Simple script to run the port 8080 forwarder in the background

# Kill any existing instances
pid_file="port_8080.pid"
if [ -f "$pid_file" ]; then
    pid=$(cat "$pid_file")
    if ps -p "$pid" > /dev/null; then
        echo "Killing existing port forwarder (PID: $pid)"
        kill -9 "$pid"
    fi
    rm -f "$pid_file"
fi

# Start the port forwarder in the background
echo "Starting port 8080 forwarder..."
python port8080.py > port8080.log 2>&1 &

# Save the PID
echo $! > "$pid_file"
echo "Port forwarder started with PID $(cat $pid_file)"
echo "Logs are in port8080.log"
