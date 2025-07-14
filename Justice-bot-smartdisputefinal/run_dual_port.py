#!/usr/bin/env python3
"""
Dual-port server script for SmartDispute.ai
This script runs the Flask application on both port 5000 and port 8080 simultaneously.
"""

import os
import sys
import time
import threading
import subprocess
import logging
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dual_port_server')

# Configuration
MAIN_PORT = 5000
REPLIT_PORT = 8080
MAIN_LOG = 'port5000.log'
REPLIT_LOG = 'port8080.log'
MAIN_APP = 'main:app'
PORT_APP = 'port8080:app'

def run_server_on_port(port, app_module, log_file):
    """Run a Flask server on the specified port"""
    logger.info(f"Starting server on port {port} with app {app_module}")
    
    # Open log files
    with open(log_file, 'a') as log:
        # Create and start the subprocess
        server_process = subprocess.Popen(
            [
                'gunicorn',
                '--bind', f'0.0.0.0:{port}',
                '--reuse-port',
                '--reload',
                app_module
            ],
            stdout=log,
            stderr=log
        )
        
    # Return the process object
    return server_process

def main():
    """Run both servers simultaneously"""
    logger.info("Starting SmartDispute.ai dual-port server")
    
    main_server = None
    replit_server = None
    
    try:
        # Start server on port 5000 (main app)
        main_server = run_server_on_port(MAIN_PORT, MAIN_APP, MAIN_LOG)
        logger.info(f"Main server started on port {MAIN_PORT} with PID {main_server.pid}")
        
        # Wait a moment for main server to start
        time.sleep(2)
        
        # Start server on port 8080 (Replit port)
        if os.path.exists('port8080.py'):
            replit_server = run_server_on_port(REPLIT_PORT, PORT_APP, REPLIT_LOG)
            logger.info(f"Replit server started on port {REPLIT_PORT} with PID {replit_server.pid}")
        else:
            logger.warning("port8080.py not found, only running on port 5000")
        
        logger.info("Both servers are running. Press Ctrl+C to stop.")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if main_server and main_server.poll() is not None:
                logger.error(f"Main server on port {MAIN_PORT} has stopped unexpectedly!")
                break
                
            if replit_server and replit_server.poll() is not None:
                logger.error(f"Replit server on port {REPLIT_PORT} has stopped unexpectedly!")
                replit_server = run_server_on_port(REPLIT_PORT, PORT_APP, REPLIT_LOG)
                logger.info(f"Restarted Replit server with PID {replit_server.pid}")
    
    except KeyboardInterrupt:
        logger.info("Shutting down servers...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Cleanup
        if main_server:
            logger.info(f"Terminating main server (PID: {main_server.pid})")
            main_server.terminate()
            
        if replit_server:
            logger.info(f"Terminating Replit server (PID: {replit_server.pid})")
            replit_server.terminate()
            
        logger.info("Servers shutdown complete")

def signal_handler(sig, frame):
    """Handle signals to properly shutdown"""
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the dual-port server
    main()