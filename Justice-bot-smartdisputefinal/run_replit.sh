#!/bin/bash
# Start script to use with Replit workflow

echo "===== SmartDispute.ai Replit Server ====="
echo "Starting on port 8080..."

# Run the ultra minimal server on port 8080
gunicorn --bind 0.0.0.0:8080 --reuse-port --reload ultra_minimal:app