#!/usr/bin/env python3
# Simple port adapter workflow for SmartDispute.ai
# This script runs in a separate Replit workflow to adapt port 8080 to 5000

import os
import sys
import time
import socket
import signal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("port_adaptor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('port_adaptor')

# Configuration
MAIN_PORT = 5000
FORWARDER_PORT = 8080

def is_port_in_use(port):
    """Check if a port is in use"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0
    except:
        return False
    finally:
        if 's' in locals():
            s.close()

def wait_for_main_app():
    """Wait for the main application to be running"""
    logger.info(f"Waiting for main application on port {MAIN_PORT}...")
    
    while not is_port_in_use(MAIN_PORT):
        logger.info("Main application not running yet. Waiting...")
        time.sleep(5)
    
    logger.info(f"Main application is running on port {MAIN_PORT}")
    return True

def start_port_adaptor():
    """Start the port adaptor using socat"""
    logger.info(f"Starting port adaptor for port {FORWARDER_PORT} -> {MAIN_PORT}")
    
    # Print important information
    logger.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not set')}")
    logger.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not set')}")
    
    # Check if socat is available
    try:
        import subprocess
        logger.info("Starting socat process...")
        cmd = f"socat TCP-LISTEN:{FORWARDER_PORT},fork TCP:localhost:{MAIN_PORT}"
        process = subprocess.Popen(cmd, shell=True)
        logger.info(f"Port adaptor started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start socat: {e}")
        return None

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for main app to be running
    wait_for_main_app()
    
    # Start port adaptor
    process = start_port_adaptor()
    if not process:
        logger.error("Failed to start port adaptor, exiting")
        return 1
    
    # Print success message
    logger.info("Port adaptor is running. Press Ctrl+C to stop.")
    
    # Keep the script running
    try:
        while True:
            # Check if main app is still running
            if not is_port_in_use(MAIN_PORT):
                logger.warning("Main application is no longer running, waiting for it to restart...")
                wait_for_main_app()
                
            # Check if adaptor process is still running
            if process.poll() is not None:
                logger.warning("Port adaptor process stopped, restarting...")
                process = start_port_adaptor()
                if not process:
                    logger.error("Failed to restart port adaptor, exiting")
                    return 1
            
            # Sleep to avoid busy-waiting
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    finally:
        if process and process.poll() is None:
            logger.info("Terminating port adaptor process...")
            process.terminate()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
