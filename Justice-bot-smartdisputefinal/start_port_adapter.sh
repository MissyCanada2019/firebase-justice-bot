#!/bin/bash
# Start the port 8080 adapter and keep it running in the background

echo "Starting port 8080 adapter..."

# Kill any existing port adapter processes
pkill -f "python simple_port_8080.py" || true

# Start the adapter in the background
python simple_port_8080.py > port_8080.log 2>&1 &

# Save the PID for later use
echo $! > port_8080_adapter.pid

echo "Port 8080 adapter started with PID $(cat port_8080_adapter.pid)"

# Monitor the adapter to make sure it stays running
while true; do
  if ! ps -p $(cat port_8080_adapter.pid) > /dev/null; then
    echo "Port adapter stopped, restarting..."
    python simple_port_8080.py > port_8080.log 2>&1 &
    echo $! > port_8080_adapter.pid
    echo "Port 8080 adapter restarted with PID $(cat port_8080_adapter.pid)"
  fi
  sleep 5
done
