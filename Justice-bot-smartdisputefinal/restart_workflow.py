"""
Restart Workflow Script for SmartDispute.ai

This script will:
1. Restart the main application workflow
2. Start the port 8080 adapter in the background
"""
import os
import sys
import time
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to restart workflows and start port adapter"""
    logger.info("Restarting SmartDispute.ai with port 8080 adapter")
    
    # Kill any existing processes
    logger.info("Stopping any existing processes...")
    try:
        subprocess.run(['pkill', '-f', 'port8080.py'], check=False)
        subprocess.run(['pkill', '-f', 'port_adapting_server.py'], check=False)
        # Don't kill gunicorn, the workflow system will restart it
    except Exception as e:
        logger.error(f"Error stopping processes: {e}")
    
    # Wait a moment for processes to stop
    time.sleep(1)
    
    # Start the port 8080 server in the background
    logger.info("Starting port 8080 server...")
    try:
        p = subprocess.Popen(['python', 'port8080.py'])
        logger.info(f"Started port 8080 server with PID: {p.pid}")
    except Exception as e:
        logger.error(f"Error starting port 8080 server: {e}")
    
    logger.info("Port 8080 server started successfully")
    logger.info("The main application should be accessible via port 8080 through Replit")

if __name__ == "__main__":
    main()