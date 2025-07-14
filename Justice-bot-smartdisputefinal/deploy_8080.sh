#!/bin/bash

# This script deploys a simple port 8080 server
# which is required for Replit web interface

echo "Starting SmartDispute.ai on port 8080..."

# First, stop any running server
pkill -f "python.*simple_8080.py" || true

# Start the server in the background
python simple_8080.py > port8080.log 2>&1 &
PORT8080_PID=$!

# Save the PID
echo $PORT8080_PID > port8080.pid

echo "Server started on port 8080 with PID $PORT8080_PID"
echo "Log file: port8080.log"
