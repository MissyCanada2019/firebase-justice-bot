#!/usr/bin/env python3
"""
Simple startup script for SmartDispute.ai
Bypasses complex initialization to get the application running
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("Starting SmartDispute.ai on port 5000...")
    
    # Simple Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )