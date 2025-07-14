#!/usr/bin/env python3
"""
Direct Flask Application Start on Port 8080
Simple solution for Replit web access
"""

import os
import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Set port from environment or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"Starting SmartDispute.ai directly on port {port}")
    
    # Run the Flask application
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        threaded=True,
        use_reloader=False
    )