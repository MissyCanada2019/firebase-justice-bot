#!/usr/bin/env python3
"""
Simple Flask server for SmartDispute.ai on port 8080
Direct Flask development server for Replit web interface compatibility
"""

from app import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting SmartDispute.ai on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True,
        use_reloader=False
    )