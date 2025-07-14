#!/usr/bin/env python3
"""
Simple port 8080 server for SmartDispute.ai
This provides direct access on port 8080 for Replit web interface
"""
import os
import sys
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app import app
    
    if __name__ == "__main__":
        logger.info("Starting SmartDispute.ai on port 8080")
        logger.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not available')}")
        
        # Run Flask app directly on port 8080
        app.run(
            host="0.0.0.0",
            port=8080,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
except ImportError as e:
    logger.error(f"Failed to import app: {e}")
    # Fallback minimal server
    from flask import Flask
    
    fallback_app = Flask(__name__)
    
    @fallback_app.route('/')
    def index():
        return """
        <h1>SmartDispute.ai</h1>
        <p>Server is starting up. Please wait a moment and refresh the page.</p>
        <script>setTimeout(() => location.reload(), 5000);</script>
        """
    
    fallback_app.run(host="0.0.0.0", port=8080, debug=False)