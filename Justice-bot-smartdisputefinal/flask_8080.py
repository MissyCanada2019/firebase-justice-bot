#!/usr/bin/env python3
"""
Direct Flask server on port 8080 for Replit web interface
This imports and runs the main application directly on port 8080
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main application
from app import app

if __name__ == "__main__":
    # Run the Flask app directly on port 8080
    app.run(host="0.0.0.0", port=8080, debug=False)