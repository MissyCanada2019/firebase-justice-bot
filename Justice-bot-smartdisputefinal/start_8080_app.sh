#!/bin/bash
# Script to start the Flask app on port 8080

echo "===== SmartDispute.ai Port 8080 App ====="

# Kill any existing processes
echo "Shutting down any existing servers..."
pkill -f gunicorn || true
pkill -f 'python.*simple_server.py' || true
pkill -f 'python.*port_8080_server.py' || true
pkill -f 'python.*port8080.py' || true
pkill -f 'python.*ultra_minimal.py' || true
sleep 1

# Start the Flask app on port 8080
echo "Starting server on port 8080..."
python -m gunicorn --bind 0.0.0.0:8080 --workers 1 --reload 'port8080:app'