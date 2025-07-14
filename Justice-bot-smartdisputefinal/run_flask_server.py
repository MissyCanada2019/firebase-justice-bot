#!/usr/bin/env python3
"""
Flask Development Server for SmartDispute.ai

This script is designed to run the Flask application using its built-in
development server, which was the configuration that was working on Railway.
"""
import os
import sys
import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Print environment for debugging
print(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not set')}")
print(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not set')}")
print(f"GOOGLE_OAUTH_CLIENT_ID: {os.environ.get('GOOGLE_OAUTH_CLIENT_ID', 'Not set')[:10]}...")
print(f"GOOGLE_OAUTH_CLIENT_SECRET: {'*' * 10 if os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET') else 'Not set'}")

if __name__ == "__main__":
    print("\n===== SmartDispute.ai Flask Development Server =====\n")
    
    # Print all registered routes for debugging
    print("\nRegistered routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ','.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"{rule.rule:40s} {methods:20s} -> {rule.endpoint}")
    
    # Start the Flask development server on port 5000
    print("\nStarting Flask development server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
