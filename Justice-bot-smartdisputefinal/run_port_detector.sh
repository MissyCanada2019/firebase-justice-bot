#!/bin/bash
# Script to run the port detector diagnostic tool

echo "===== SmartDispute.ai Port Detector ====="
echo "Starting port detector diagnostic tool..."

# Kill any existing processes
echo "Shutting down any existing servers..."
pkill -f gunicorn || true
pkill -f 'python.*server.py' || true
pkill -f 'python.*port_detector.py' || true
sleep 1

# Start the port detector
echo "Starting port detector..."
python port_detector.py