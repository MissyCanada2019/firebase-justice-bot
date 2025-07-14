#!/usr/bin/env python3
"""
Port 8080 Runner for Replit Web Access
Starts the Flask application on port 8080 for Replit compatibility
"""

import subprocess
import sys
import time
import logging
import signal
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_port_available(port):
    """Check if a port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def main():
    """Start the application on port 8080"""
    logger.info("Starting SmartDispute.ai on port 8080 for Replit web access")
    
    # Check if port 8080 is available
    if not check_port_available(8080):
        logger.warning("Port 8080 is in use, attempting to clear it")
        subprocess.run(["pkill", "-f", "port.*8080"], capture_output=True)
        time.sleep(2)
    
    # Start gunicorn on port 8080
    cmd = [
        "gunicorn", 
        "--bind", "0.0.0.0:8080",
        "--workers", "1",
        "--timeout", "120",
        "--keep-alive", "2",
        "--max-requests", "1000",
        "--max-requests-jitter", "100",
        "main:app"
    ]
    
    try:
        logger.info("Starting gunicorn on port 8080...")
        process = subprocess.Popen(cmd)
        
        # Set up signal handling
        def signal_handler(sig, frame):
            logger.info("Shutting down...")
            process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Wait for process
        process.wait()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()