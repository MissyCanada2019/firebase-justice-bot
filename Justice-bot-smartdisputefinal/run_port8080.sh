#!/bin/bash

# Kill any existing simple forwarder process
pkill -f "python simple_forwarder.py" > /dev/null 2>&1

# Start the port forwarder in the background
echo "Starting port 8080 forwarder in the background..."
nohup python simple_forwarder.py > port8080.log 2>&1 &

# Store the PID for future reference
echo $! > port8080.pid

echo "Port 8080 forwarder started with PID $(cat port8080.pid)"
echo "The forwarder will now forward requests from port 8080 to port 5000."
echo "You can check port8080.log for activity."
