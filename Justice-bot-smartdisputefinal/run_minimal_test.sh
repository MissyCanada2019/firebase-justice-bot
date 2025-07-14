#!/bin/bash
# Script to run the minimal test server for connectivity testing

echo "===== SmartDispute.ai Minimal Test Server ====="
echo "Starting minimal test server on ports 5000 and 8080..."

# Kill any existing server processes
echo "Shutting down any existing server processes..."
pkill -f gunicorn || true
pkill -f 'python.*server.py' || true
sleep 1

# Start the minimal test server
echo "Starting minimal test server..."
python minimal_test_server.py