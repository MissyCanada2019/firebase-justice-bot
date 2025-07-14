#!/bin/bash
# Optimized startup script for SmartDispute.ai on Replit

echo "===== SmartDispute.ai Optimized Starter ====="
echo "Using enhanced gunicorn configuration..."

# Kill any existing gunicorn processes
echo "Checking for existing processes..."
pkill -f gunicorn || true
sleep 1

# Start with optimized gunicorn configuration
echo "Starting server with optimized gunicorn config..."
gunicorn -c gunicorn_config.py main:app