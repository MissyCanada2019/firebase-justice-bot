#!/usr/bin/env python3
"""
Flask Development Server Launcher
This script runs the Flask application using the built-in development server
instead of gunicorn, matching the configuration that worked on Railway.
"""
import os
import sys
import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("\n===== Starting Flask Development Server =====")
    print(f"Domain: {os.environ.get('REPLIT_DEV_DOMAIN', 'unknown')}")
    print("================================================\n")
    
    # Print all registered routes for debugging
    print("\nRegistered routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ','.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"{rule.rule:40s} {methods:20s} -> {rule.endpoint}")
    
    # Start the server with Flask's built-in development server
    # This matches the configuration that was working on Railway
    print("\nStarting Flask development server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
