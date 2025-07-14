#!/bin/bash
# Run the Flask app on port 8080 for testing Replit connectivity

echo "===== SmartDispute.ai Flask Server on Port 8080 ====="
echo "Starting Flask server on port 8080..."

# Kill any existing processes on port 5000 and 8080
echo "Checking for existing processes..."
pkill -f gunicorn || true
pkill -f 'python.*simple_server.py' || true
pkill -f 'python.*port_8080_server.py' || true
pkill -f 'python.*main_port_8080.py' || true
sleep 1

# Start using gunicorn to match the workflow configuration
echo "Starting gunicorn on port 8080..."
gunicorn --bind 0.0.0.0:8080 --reuse-port --reload 'main_port_8080:app'