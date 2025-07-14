#!/bin/bash
# Port 8080 Server Runner for SmartDispute.ai

# Kill any running instances
pkill -f "python run_direct_8080.py" > /dev/null 2>&1

echo "Starting SmartDispute.ai on port 8080..."
echo "-----------------------------------------"
python run_direct_8080.py
