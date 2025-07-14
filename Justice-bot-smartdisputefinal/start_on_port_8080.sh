#!/bin/bash
# Startup script for SmartDispute.ai that runs on port 8080
# This script is used by the Replit workflow

echo "==================================================="
echo "    SmartDispute.ai Starting on Port 8080"
echo "==================================================="

# Start the application on port 8080 using gunicorn
gunicorn --bind 0.0.0.0:8080 --reuse-port --reload main_direct:app
