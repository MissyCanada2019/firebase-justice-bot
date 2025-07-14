#!/bin/bash
# Start SmartDispute.ai web server on port 8080 for Replit accessibility

echo "Starting SmartDispute.ai web server on port 8080..."

# Kill any existing processes on port 8080
pkill -f "8080" 2>/dev/null

# Start gunicorn on port 8080
exec gunicorn \
    --bind 0.0.0.0:8080 \
    --workers 1 \
    --timeout 300 \
    --keep-alive 60 \
    --max-requests 1000 \
    --worker-class sync \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    main:app