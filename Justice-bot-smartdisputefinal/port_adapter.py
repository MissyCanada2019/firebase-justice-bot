#!/usr/bin/env python3

"""
Port adapter for SmartDispute.ai

This script makes sure port 8080 is accessible by checking if the port is available
and starting a port forwarder if needed.

It's designed to be run as a workflow in Replit that starts automatically with the main app.
"""

import os
import time
import subprocess
import logging
import sys
import signal
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='port_adapter.log',
    filemode='a'
)
logger = logging.getLogger('port_adapter')

# Add a stream handler for console output
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

# Configuration
CHECK_INTERVAL = 10  # seconds between checks
PORT = 8080
FORWARDER_SCRIPT = "simple_port8080.py"
PID_FILE = "port_adapter.pid"
FORWARDER_PID_FILE = "port8080.pid"

# Global variables
forwarder_process = None

# Print startup information
print(f"Starting port adapter for SmartDispute.ai")
print(f"This adapter will ensure port {PORT} is accessible")
print(f"Check interval: {CHECK_INTERVAL} seconds")
print(f"Forwarder script: {FORWARDER_SCRIPT}")

def is_port_in_use(port):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_forwarder():
    """Start the port forwarder process"""
    global forwarder_process
    
    # First, stop any existing process
    stop_forwarder()
    
    # Start the new process
    try:
        logger.info(f"Starting port forwarder: {FORWARDER_SCRIPT}")
        forwarder_process = subprocess.Popen(
            ["python", FORWARDER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Save the PID to a file
        with open(FORWARDER_PID_FILE, "w") as f:
            f.write(str(forwarder_process.pid))
            
        logger.info(f"Port forwarder started with PID {forwarder_process.pid}")
        return True
    except Exception as e:
        logger.error(f"Error starting port forwarder: {e}")
        return False

def stop_forwarder():
    """Stop the port forwarder process"""
    global forwarder_process
    
    # Try to stop using the PID file
    if os.path.exists(FORWARDER_PID_FILE):
        try:
            with open(FORWARDER_PID_FILE, "r") as f:
                pid = int(f.read().strip())
                
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info(f"Sent SIGTERM to forwarder process with PID {pid}")
                time.sleep(1)
                
                # If still running, force kill
                try:
                    os.kill(pid, 0)  # Check if process exists
                    os.kill(pid, signal.SIGKILL)
                    logger.info(f"Sent SIGKILL to forwarder process with PID {pid}")
                except OSError:
                    pass  # Process no longer exists
            except OSError as e:
                logger.info(f"Process with PID {pid} not found: {e}")
                
            # Remove the PID file
            os.remove(FORWARDER_PID_FILE)
        except Exception as e:
            logger.error(f"Error stopping forwarder using PID file: {e}")
    
    # Also try to stop using our process reference
    if forwarder_process:
        try:
            forwarder_process.terminate()
            logger.info(f"Terminated forwarder process with PID {forwarder_process.pid}")
            time.sleep(1)
            
            # If still running, force kill
            if forwarder_process.poll() is None:
                forwarder_process.kill()
                logger.info(f"Killed forwarder process with PID {forwarder_process.pid}")
        except Exception as e:
            logger.error(f"Error terminating forwarder process: {e}")
    
    # Also try pkill by name
    try:
        subprocess.run(["pkill", "-f", FORWARDER_SCRIPT], check=False)
    except Exception as e:
        logger.error(f"Error using pkill: {e}")

def cleanup():
    """Clean up before exit"""
    logger.info("Cleaning up before exit")
    stop_forwarder()
    
    # Remove our PID file
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def signal_handler(sig, frame):
    """Handle signals gracefully"""
    logger.info(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)

def main():
    """Main function"""
    # Register signal handlers and exit handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    atexit.register(cleanup)
    
    # Save our PID to a file
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    
    logger.info("Starting port adapter")
    
    # Main loop
    while True:
        # Check if port 8080 is in use
        if not is_port_in_use(PORT):
            logger.info(f"Port {PORT} is not in use, starting forwarder")
            start_forwarder()
        else:
            logger.info(f"Port {PORT} is in use")
        
        # Check if our forwarder process is still running
        if forwarder_process and forwarder_process.poll() is not None:
            logger.warning(f"Forwarder process exited with code {forwarder_process.returncode}, restarting")
            start_forwarder()
        
        # Wait before next check
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)
