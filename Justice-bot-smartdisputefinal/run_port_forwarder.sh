#!/bin/bash

# Kill any existing port forwarder process
pkill -f "python port_forwarder.py" > /dev/null 2>&1

# Start the port forwarder in the background
echo "Starting port forwarder in the background..."
nohup python port_forwarder.py > port_forwarder.log 2>&1 &

# Store the PID for future reference
echo $! > port_forwarder.pid

echo "Port forwarder started with PID $(cat port_forwarder.pid)"
echo "The port forwarder will now forward requests from port 8080 to port 5000."
echo "You can check port_forwarder.log for activity."
