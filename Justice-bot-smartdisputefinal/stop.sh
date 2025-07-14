#!/bin/bash

# Stop all running SmartDispute.ai processes

echo "Stopping all SmartDispute.ai processes..."

# Stop any running gunicorn processes
pkill -f gunicorn

# Stop any running Python processes related to the app
pkill -f "python.*port8080"
pkill -f "python.*run_port8080"
pkill -f "python.*direct_port8080"

echo "All processes stopped."
