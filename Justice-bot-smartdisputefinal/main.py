#!/usr/bin/env python3
"""
Justice-Bot - Canadian Legal Assistant Platform
Main entry point for the Flask application
"""

import os
from app import app

if __name__ == '__main__':
    print("Starting Justice-Bot Canadian Legal Assistant...")
    port = int(os.environ.get("PORT", 5000))  # Get dynamic port from Railway
    app.run(host='0.0.0.0', port=port, debug=True)
