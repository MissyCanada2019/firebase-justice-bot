#!/usr/bin/env python3

"""
Port Forwarder Workflow for SmartDispute.ai

This script is designed to be started as a Replit workflow.
It starts the port 8080 forwarder service that redirects traffic to port 5000.
"""

import os
import sys
import subprocess
import time
import signal
import atexit

# Configuration
FORWARDER_SCRIPT = "simple_port8080.py"
LOG_FILE = "port_forwarder_workflow.log"
PID_FILE = "port_forwarder_workflow.pid"

# Global variables
forwarder_process = None

def setup_logging():
    """Set up logging to file and console"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('port_forwarder_workflow')

# Set up logging
logger = setup_logging()

def cleanup():
    """Clean up on exit"""
    global forwarder_process
    logger.info("Cleaning up before exit")
    
    if forwarder_process:
        try:
            logger.info(f"Terminating port forwarder process (PID: {forwarder_process.pid})")
            forwarder_process.terminate()
            time.sleep(1)
            
            # Force kill if still running
            if forwarder_process.poll() is None:
                logger.info(f"Force killing port forwarder process (PID: {forwarder_process.pid})")
                forwarder_process.kill()
        except Exception as e:
            logger.error(f"Error stopping port forwarder: {e}")
    
    # Remove PID file
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def signal_handler(sig, frame):
    """Handle signals gracefully"""
    logger.info(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)

def start_forwarder():
    """Start the port forwarder process"""
    global forwarder_process
    
    try:
        logger.info(f"Starting port forwarder: {FORWARDER_SCRIPT}")
        forwarder_process = subprocess.Popen(
            ["python", FORWARDER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        logger.info(f"Port forwarder started with PID {forwarder_process.pid}")
        return True
    except Exception as e:
        logger.error(f"Error starting port forwarder: {e}")
        return False

def log_output():
    """Log the output from the forwarder process"""
    global forwarder_process
    
    if forwarder_process and forwarder_process.stdout:
        for line in forwarder_process.stdout:
            logger.info(f"Forwarder output: {line.strip()}")

def monitor_forwarder():
    """Monitor the forwarder process and restart if needed"""
    global forwarder_process
    
    while True:
        # Check if the process is still running
        if forwarder_process and forwarder_process.poll() is not None:
            logger.warning(f"Port forwarder process exited with code {forwarder_process.returncode}, restarting")
            start_forwarder()
        
        # Wait before checking again
        time.sleep(10)

def main():
    """Main function"""
    # Register signal handlers and exit handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    atexit.register(cleanup)
    
    # Save our PID
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    
    logger.info("Starting port forwarder workflow")
    print(f"Starting port forwarder workflow (PID: {os.getpid()})")
    
    # Start the port forwarder
    if not start_forwarder():
        logger.error("Failed to start port forwarder, exiting")
        return 1
    
    # Monitor the forwarder in a loop
    try:
        monitor_forwarder()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")
    except Exception as e:
        logger.error(f"Error in monitor loop: {e}")
    finally:
        cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
