#!/bin/bash
# Run the ultra minimal Flask server for testing

echo "===== SmartDispute.ai Ultra Minimal Tester ====="
echo "Starting minimal server on port 5000..."

# Kill any existing processes
echo "Checking for existing processes..."
pkill -f gunicorn || true
sleep 1

# Start the minimal Flask app
echo "Starting minimal Flask app..."
gunicorn --bind 0.0.0.0:5000 ultra_minimal:app