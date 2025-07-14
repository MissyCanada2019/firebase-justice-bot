#!/usr/bin/env python3
"""
Direct Port 8080 Runner for SmartDispute.ai

This script runs the Flask application directly on port 8080
without any dependencies on gunicorn or other complex servers.
"""
import os
import sys

# Import the Flask app
try:
    from main import app
    print("Successfully imported Flask app from main.py")
except ImportError as e:
    print(f"Error importing app from main.py: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting SmartDispute.ai application on port 8080...")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app directly on port 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
