#!/bin/bash
# Start the auto port adapter in the background
# This script can be run at Replit startup time

echo "Starting SmartDispute.ai Auto Port Adapter..."

# Check if it's already running
if [ -f "auto_port_adapter.pid" ]; then
  PID=$(cat auto_port_adapter.pid)
  if ps -p $PID > /dev/null; then
    echo "Auto Port Adapter is already running with PID $PID"
    exit 0
  else
    echo "Removing stale PID file"
    rm auto_port_adapter.pid
  fi
fi

# Start the auto port adapter in the background
nohup python auto_port_adapter.py > auto_port_adapter.log 2>&1 &

echo "Auto Port Adapter started in the background"
echo "This will automatically manage the port 8080 adapter"
echo "See auto_port_adapter.log for details"