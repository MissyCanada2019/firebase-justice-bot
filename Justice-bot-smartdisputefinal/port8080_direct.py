"""
Direct port 8080 server for SmartDispute.ai
This script runs Flask directly on port 8080 as required by Replit
"""
import os
import sys
from app import app

if __name__ == "__main__":
    print("Starting Flask server directly on port 8080...")
    # Force the app to run on port 8080
    app.run(host="0.0.0.0", port=8080, debug=False)