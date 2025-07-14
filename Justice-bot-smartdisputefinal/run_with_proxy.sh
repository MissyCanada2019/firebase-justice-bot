#!/bin/bash
# Run SmartDispute.ai with port 8080 proxy
# This script starts the main application on port 5000 and a proxy on port 8080

echo "====================================================="
echo "    SmartDispute.ai with Port 8080 Proxy"
echo "====================================================="
echo "This script runs the main application on port 5000 and a proxy on port 8080"
echo ""

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f "gunicorn.*main" || true
pkill -f "python.*port_proxy.py" || true

# Start the main application on port 5000
echo "Starting main application on port 5000..."
nohup gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app > port5000.log 2>&1 &
echo "Main application started with PID: $!"

# Wait a moment to ensure port 5000 is running
sleep 3

# Make the port_proxy.py executable
chmod +x port_proxy.py

# Start the port 8080 proxy
echo "Starting port 8080 proxy..."
nohup python port_proxy.py > port8080.log 2>&1 &
echo "Port 8080 proxy started with PID: $!"

echo ""
echo "SmartDispute.ai is running!"
echo "- Main application on port 5000 (port5000.log)"
echo "- Proxy on port 8080 (port8080.log)"
echo "====================================================="

# Wait a moment for servers to start up
sleep 5

# Test both ports
echo "Testing port 5000:"
curl -s http://localhost:5000/health || echo "Port 5000 not responding"
echo -e "\n\nTesting port 8080:"
curl -s http://localhost:8080/health || echo "Port 8080 not responding"
echo -e "\n\nBoth servers should now be running."