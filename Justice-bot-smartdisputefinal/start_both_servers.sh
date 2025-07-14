#!/bin/bash
# Start both the main application and the port 8080 adapter

# Kill any existing processes
echo "Cleaning up any existing processes..."
pkill -f "python.*port8080" || true

# Add to .bash_profile to automatically start on login
if ! grep -q "port8080_app.py" ~/.bash_profile; then
    echo "Adding port 8080 adapter to .bash_profile for automatic startup"
    echo "nohup python port8080_app.py > port8080_app.log 2>&1 &" >> ~/.bash_profile
fi

# Start the port 8080 adapter in the background
echo "Starting port 8080 adapter..."
nohup python port8080_app.py > port8080_app.log 2>&1 &
PORT_ADAPTER_PID=$!

# Save the PID for later cleanup
echo $PORT_ADAPTER_PID > port8080_app.pid

# Log the startup
echo "Port 8080 adapter started with PID: $PORT_ADAPTER_PID"
echo "SmartDispute.ai should be accessible on both port 5000 and 8080"

# Wait a moment to check if the process is still running
sleep 2
if ps -p $PORT_ADAPTER_PID > /dev/null; then
    echo "Port 8080 adapter is running successfully!"
else
    echo "Warning: Port 8080 adapter may have failed to start. Check port8080_app.log for details."
    tail -20 port8080_app.log
fi

# Create a cleanup function
cleanup() {
    echo "Cleaning up processes..."
    if [ -f port8080_app.pid ]; then
        PORT_PID=$(cat port8080_app.pid)
        kill $PORT_PID 2>/dev/null || true
        rm port8080_app.pid
    fi
    exit 0
}

# Register the cleanup function for signals
trap cleanup SIGINT SIGTERM

echo "Done. The port 8080 adapter is running in the background."
echo "Use 'ps -ef | grep python' to check running processes."
echo "Use 'cat port8080_app.log' to check the port adapter's log file."
