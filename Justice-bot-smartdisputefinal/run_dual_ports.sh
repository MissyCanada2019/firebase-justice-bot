#!/bin/bash
# Script to run the dual port application for SmartDispute.ai

# Kill any existing instances
pid_file="dual_port.pid"
if [ -f "$pid_file" ]; then
    pid=$(cat "$pid_file")
    if ps -p "$pid" > /dev/null; then
        echo "Killing existing dual port application (PID: $pid)"
        kill -9 "$pid"
    fi
    rm -f "$pid_file"
fi

# Stop any running port 8080 forwarders
if [ -f "port_8080.pid" ]; then
    pid=$(cat "port_8080.pid")
    if ps -p "$pid" > /dev/null; then
        echo "Killing existing port 8080 forwarder (PID: $pid)"
        kill -9 "$pid"
    fi
    rm -f "port_8080.pid"
fi

# Start the dual port application
echo "Starting dual port application..."
python dual_port_application.py > dual_port.log 2>&1 &

# Save the PID
echo $! > "$pid_file"
echo "Dual port application started with PID $(cat $pid_file)"
echo "Logs are in dual_port.log"
