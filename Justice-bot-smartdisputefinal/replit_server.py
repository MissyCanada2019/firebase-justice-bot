#!/usr/bin/env python3
"""
Replit-specific server for SmartDispute.ai
This script runs the app on port 8080 directly (as required by Replit)
and optionally starts a proxy/forwarder on port 5000 as well.
"""
import os
import sys
import threading
import time
import logging
import subprocess
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Server configuration
PORT_8080 = 8080
PORT_5000 = 5000

def signal_handler(sig, frame):
    """Handle signals to properly clean up"""
    logging.info("Shutting down...")
    # Kill any gunicorn processes
    try:
        subprocess.run(["pkill", "-f", "gunicorn"], check=False)
        logging.info("Stopped gunicorn processes")
    except Exception as e:
        logging.warning(f"Error stopping gunicorn: {e}")
    
    sys.exit(0)

def start_server():
    """
    Start the app server on port 8080
    """
    # Print environment info
    logging.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
    logging.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not found')}")
    logging.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not found')}")
    logging.info(f"Starting SmartDispute.ai server on port {PORT_8080}")
    
    # Stop any existing gunicorn processes
    try:
        subprocess.run(["pkill", "-f", "gunicorn"], check=False)
        logging.info("Stopped existing gunicorn processes")
        time.sleep(1)
    except Exception as e:
        logging.warning(f"Error stopping existing processes: {e}")
    
    # Start gunicorn on port 8080
    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{PORT_8080}",
        "--reuse-port",
        "--reload",
        "app:app"
    ]
    
    try:
        server_process = subprocess.Popen(cmd)
        logging.info(f"Started server on port {PORT_8080} with PID {server_process.pid}")
        return server_process
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        return None

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server
    server_process = start_server()
    if not server_process:
        sys.exit(1)
    
    # Wait for server to exit
    try:
        server_process.wait()
        logging.warning(f"Server exited with code {server_process.returncode}")
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    finally:
        # Make sure to clean up
        try:
            subprocess.run(["pkill", "-f", "gunicorn"], check=False)
        except:
            pass

if __name__ == "__main__":
    main()