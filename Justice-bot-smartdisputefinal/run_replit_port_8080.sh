#!/bin/bash
# Run the Replit port 8080 adapter for SmartDispute.ai

echo "===================================================="
echo "    SmartDispute.ai Replit Port 8080 Adapter"
echo "===================================================="
echo "This script sets up port 8080 forwarding for Replit"
echo ""

# Kill any existing port adapters/forwarders
echo "Cleaning up existing processes..."

# Kill any existing port forwarders
pkill -f "python.*port8080.py" || true
pkill -f "python.*port_forwarder.py" || true
pkill -f "python.*simple_port_forward.py" || true
pkill -f "python.*auto_port_forward.py" || true
pkill -f "python.*auto_port_adapter.py" || true
pkill -f "python.*minimal_redirect.py" || true
pkill -f "python.*replit_port_adapter.py" || true
pkill -f "python.*replit_port_8080.py" || true

# Start the flask-based port adapter
echo "Starting Flask-based port 8080 adapter..."
python replit_port_8080.py &
ADAPTER_PID=$!
echo "Port adapter started with PID: $ADAPTER_PID"
echo $ADAPTER_PID > replit_port_8080.pid

echo ""
echo "Flask port 8080 adapter is now running!"
echo "Port 8080 is being forwarded to the main application on port 5000"
echo "===================================================="