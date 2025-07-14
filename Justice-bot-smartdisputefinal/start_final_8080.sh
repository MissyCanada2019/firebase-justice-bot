#!/bin/bash

# Start script for the final port 8080 server
# This script runs a pure Python HTTP server on port 8080

echo "Starting SmartDispute.ai server on port 8080..."

# 1. Kill any existing servers
pkill -f "python.*final_8080.py" || true
pkill -f "gunicorn" || true
pkill -f "python.*pure_8080.py" || true

# 2. Create log directory
mkdir -p logs

# 3. Start the server
python final_8080.py > logs/final_8080.log 2>&1 &
FINAL_PID=$!
echo $FINAL_PID > final_8080.pid

echo "Final server started with PID $FINAL_PID"
echo "Log file: logs/final_8080.log"
