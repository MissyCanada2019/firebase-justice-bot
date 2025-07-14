#!/usr/bin/env python3
"""
Run the direct port 8080 application with gunicorn

This is a simple script to run the main_8080_direct.py application
with gunicorn on port 8080.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_direct():
    """Run the direct port 8080 application"""
    try:
        port = 8080
        logger.info(f"Starting direct port {port} application")
        
        # We can run the Python file directly for simplicity
        cmd = ["python", "main_8080_direct.py"]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.run(cmd)
        return process.returncode
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_direct())
