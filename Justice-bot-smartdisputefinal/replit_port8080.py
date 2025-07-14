#!/usr/bin/env python3
"""
Direct Port 8080 Access for Replit
Runs Flask application directly on port 8080 for Replit web interface
"""

from app import app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting SmartDispute.ai on port 8080 for Replit access")
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)