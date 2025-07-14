#!/bin/bash
# Script to run the ultra-minimal HTTP server

echo "===== SmartDispute.ai Ultra-Minimal Server ====="
echo "Starting ultra-minimal HTTP server on ports 5000 and 8080..."

# Kill any existing processes
echo "Shutting down any existing servers..."
pkill -f gunicorn || true
pkill -f 'python.*server.py' || true
pkill -f 'python.*port_8080_server.py' || true
pkill -f 'python.*port8080.py' || true
pkill -f 'python.*ultra_minimal.py' || true
pkill -f 'python.*dual_port_server.py' || true
sleep 1

# Start the ultra-minimal server
echo "Starting ultra-minimal server..."
python ultra_minimal.py