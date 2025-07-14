#!/usr/bin/env python3
"""
Auto-restarting port forwarder for SmartDispute.ai
This script monitors the main application on port 5000 and
automatically starts/restarts the port 8080 forwarder as needed
"""

import os
import time
import socket
import subprocess
import signal
import sys
import logging
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='auto_port_forward.log',
    filemode='a'
)
logger = logging.getLogger('auto_port_forward')

# Configuration
MAIN_PORT = 5000
FORWARD_PORT = 8080
CHECK_INTERVAL = 5  # seconds

# Global variables
forwarder_process = None
running = True

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_forwarder():
    """Start the port forwarder process"""
    global forwarder_process
    
    # Check if we already have a running forwarder
    if forwarder_process and forwarder_process.poll() is None:
        logger.info("Forwarder already running")
        return
    
    # Start the simple port forward script
    try:
        logger.info("Starting port forwarder...")
        forwarder_process = subprocess.Popen(
            ["python", "simple_port_forward.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Save PID to file
        with open('auto_port_forward.pid', 'w') as f:
            f.write(str(os.getpid()))
            
        with open('port_forwarder.pid', 'w') as f:
            f.write(str(forwarder_process.pid))
            
        logger.info(f"Port forwarder started with PID {forwarder_process.pid}")
    except Exception as e:
        logger.error(f"Failed to start forwarder: {e}")

def stop_forwarder():
    """Stop the port forwarder process"""
    global forwarder_process
    
    if forwarder_process and forwarder_process.poll() is None:
        logger.info(f"Stopping port forwarder (PID: {forwarder_process.pid})")
        try:
            forwarder_process.terminate()
            forwarder_process.wait(timeout=5)
        except:
            # Force kill if termination fails
            try:
                forwarder_process.kill()
            except:
                pass
        
        logger.info("Port forwarder stopped")
        forwarder_process = None

def check_and_update():
    """Check if main app is running and start/stop port forwarder as needed"""
    main_running = is_port_in_use(MAIN_PORT)
    forwarder_running = forwarder_process and forwarder_process.poll() is None
    
    if main_running and not forwarder_running:
        # Main app is running but forwarder is not - start it
        logger.info("Main application is running, but forwarder is not")
        start_forwarder()
    elif not main_running and forwarder_running:
        # Main app is not running but forwarder is - stop it
        logger.info("Main application is not running, stopping forwarder")
        stop_forwarder()
    elif main_running and forwarder_running:
        # Both running - check if forwarder is responsive
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', FORWARD_PORT))
                if result != 0:
                    logger.warning("Port forwarder is not responding, restarting")
                    stop_forwarder()
                    start_forwarder()
        except:
            pass

def cleanup():
    """Clean up on script exit"""
    global running
    running = False
    logger.info("Cleaning up...")
    stop_forwarder()
    
    # Remove PID files
    try:
        os.remove('auto_port_forward.pid')
    except:
        pass
        
    try:
        os.remove('port_forwarder.pid')
    except:
        pass
    
    logger.info("Cleanup complete")

def signal_handler(sig, frame):
    """Handle signals to properly clean up"""
    logger.info(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function
    atexit.register(cleanup)
    
    logger.info("Starting auto port forwarder...")
    logger.info(f"Monitoring port {MAIN_PORT} and forwarding to port {FORWARD_PORT}")
    logger.info(f"Auto port forwarder PID: {os.getpid()}")
    
    # Save PID to file
    with open('auto_port_forward.pid', 'w') as f:
        f.write(str(os.getpid()))
    
    # Main loop
    while running:
        try:
            check_and_update()
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()