#!/bin/bash
# Run SmartDispute.ai Combined Server

echo "====================================================="
echo "    SmartDispute.ai Combined Server"
echo "====================================================="
echo "This script runs the application on both port 5000 and port 8080"
echo ""

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f "python.*combined_server.py" || true
pkill -f "python.*port8080.py" || true
pkill -f "python.*simple_port_forward.py" || true
pkill -f "python.*minimal_redirect.py" || true

# Make sure the script is executable
chmod +x combined_server.py

# Start the combined server
echo "Starting combined server..."
python combined_server.py > combined_server.log 2>&1 &
SERVER_PID=$!
echo "Combined server started with PID: $SERVER_PID"
echo $SERVER_PID > combined_server.pid

echo ""
echo "Combined server is active!"
echo "Serving on both port 5000 and port 8080"
echo "Server log: combined_server.log"
echo "====================================================="