#!/bin/bash
# Run SmartDispute.ai auto-restarting port forwarder

echo "===================================================="
echo "    SmartDispute.ai Auto Port Forwarder"
echo "===================================================="
echo "This script automatically manages port forwarding based on main app status"
echo ""

# Kill any existing auto port forwarder
echo "Cleaning up existing processes..."
if [ -f auto_port_forward.pid ]; then
    echo "Stopping existing auto port forwarder..."
    PID=$(cat auto_port_forward.pid)
    kill -15 $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
    rm -f auto_port_forward.pid
fi

# Kill any existing port forwarders
pkill -f "python.*simple_port_forward.py" || true
pkill -f "python.*port_forwarder.py" || true
pkill -f "python.*port8080.py" || true
pkill -f "python.*minimal_redirect.py" || true

# Make sure scripts are executable
chmod +x auto_port_forward.py
chmod +x simple_port_forward.py

# Start the auto port forwarder
echo "Starting auto port forwarder..."
python auto_port_forward.py > /dev/null 2>&1 &
FORWARDER_PID=$!
echo "Auto port forwarder started with PID: $FORWARDER_PID"
echo $FORWARDER_PID > auto_port_forward.pid

echo ""
echo "Auto port forwarding is active!"
echo "Monitoring port 5000 and forwarding to port 8080"
echo "Changes to main app status will be automatically handled"
echo "Log file: auto_port_forward.log"
echo "===================================================="