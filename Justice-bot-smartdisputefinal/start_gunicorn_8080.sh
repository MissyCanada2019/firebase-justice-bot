#!/bin/bash

# Start script for running Gunicorn directly on port 8080
# This script uses a custom Gunicorn configuration

echo "Starting SmartDispute.ai with Gunicorn on port 8080..."

# 1. Create logs directory if it doesn't exist
mkdir -p logs

# 2. Kill any existing processes
pkill -f "gunicorn" || true

# 3. Start Gunicorn with the custom configuration
gunicorn main:app -c gunicorn_config.py --daemon

echo "Gunicorn started in daemon mode on port 8080"
echo "Check logs/gunicorn.log for details"
