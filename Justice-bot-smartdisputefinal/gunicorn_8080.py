#!/usr/bin/env python3
"""
Gunicorn server script for SmartDispute.ai on port 8080

This script runs the application using Gunicorn on port 8080
which is required by Replit for web access.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_gunicorn():
    """
    Run the application with gunicorn on port 8080
    """
    try:
        # Port 8080 is required for Replit web access
        port = 8080
        logger.info(f"Starting SmartDispute.ai with Gunicorn on port {port}...")
        
        # Build the command to run gunicorn
        cmd = [
            "gunicorn",
            "--bind", f"0.0.0.0:{port}",
            "--reuse-port",
            "--reload",
            "main_8080:app"
        ]
        
        # Execute gunicorn
        process = subprocess.run(cmd)
        return process.returncode
    
    except Exception as e:
        logger.error(f"Error starting Gunicorn: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_gunicorn())
