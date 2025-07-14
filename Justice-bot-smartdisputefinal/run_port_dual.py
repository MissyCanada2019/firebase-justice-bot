#!/usr/bin/env python3
"""
Dual Port Runner for SmartDispute.ai

This script runs the main application on port 5000
and a redirecting server on port 8080 for Replit compatibility.
"""

import threading
import time
import sys
import os

# Import the main Flask application
try:
    from main import app as main_app
    print("Successfully imported main application")
except ImportError:
    print("Error: Could not import main application from main.py")
    sys.exit(1)

# Create a simple Flask app for port 8080 that redirects to the main app
from flask import Flask, redirect

redirect_app = Flask(__name__)

@redirect_app.route('/', defaults={'path': ''})
@redirect_app.route('/<path:path>')
def catch_all(path):
    """Redirect all traffic to the main application URL"""
    target = f"http://localhost:5000/{path}"
    return redirect(target)

def run_main_app():
    """Run the main application on port 5000"""
    print("Starting main application on port 5000...")
    main_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def run_redirect_app():
    """Run the redirecting application on port 8080"""
    print("Starting redirecting application on port 8080...")
    redirect_app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

def main():
    """Main function"""
    # Create threads for both applications
    main_thread = threading.Thread(target=run_main_app)
    redirect_thread = threading.Thread(target=run_redirect_app)
    
    # Start both applications
    main_thread.start()
    print("Main application thread started")
    
    # Wait a bit for the main app to start
    time.sleep(2)
    
    redirect_thread.start()
    print("Redirect application thread started")
    
    # Wait for both threads to complete (which they won't unless there's an error)
    try:
        main_thread.join()
        redirect_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down applications...")
        sys.exit(0)

if __name__ == "__main__":
    main()
