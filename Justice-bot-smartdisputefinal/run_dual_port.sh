#!/bin/bash
# Run SmartDispute.ai Dual Port Server

echo "===================================================="
echo "    SmartDispute.ai Dual Port Server"
echo "===================================================="
echo "This script runs the application on both port 5000 and port 8080"
echo ""

# Kill any existing dual port processes
echo "Cleaning up existing processes..."
if [ -f dual_port_server.pid ]; then
    echo "Stopping existing dual port server..."
    PID=$(cat dual_port_server.pid)
    kill -15 $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
    rm -f dual_port_server.pid
fi

# Kill any other port forwarders
pkill -f "python.*port8080.py" || true
pkill -f "python.*port_forwarder.py" || true
pkill -f "python.*simple_port_forward.py" || true
pkill -f "python.*minimal_redirect.py" || true

# Make sure the script is executable
chmod +x dual_port_server.py

# Start the dual port server
echo "Starting dual port server..."
python dual_port_server.py > dual_port_server.log 2>&1 &
SERVER_PID=$!
echo "Dual port server started with PID: $SERVER_PID"
echo $SERVER_PID > dual_port_server.pid

echo ""
echo "Dual port server is active!"
echo "Serving on both port 5000 and port 8080"
echo "Server log: dual_port_server.log"
echo "Port 5000 log: port5000.log"
echo "Port 8080 log: port8080.log"
echo "====================================================="