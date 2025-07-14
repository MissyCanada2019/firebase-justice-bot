#!/usr/bin/env python3
"""
Direct Port 8080 Workflow for SmartDispute.ai

This script helps manage the direct port 8080 workflow for SmartDispute.ai
by running the application on port 8080 directly, as required by Replit.
"""
import os
import sys
import logging
import subprocess
import signal
import time

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('port8080')

# Global process variable
main_process = None

def cleanup():
    """Clean up by stopping any running process"""
    global main_process
    if main_process:
        logger.info("Stopping server process")
        try:
            main_process.terminate()
            main_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Process did not terminate gracefully, forcing kill")
            main_process.kill()
        except Exception as e:
            logger.error(f"Error stopping process: {e}")
        main_process = None

def signal_handler(sig, frame):
    """Handle signals to properly clean up"""
    logger.info(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)

def start_server():
    """Start the server on port 8080"""
    global main_process
    try:
        logger.info("Starting SmartDispute.ai on port 8080")
        env = os.environ.copy()
        
        # Use python to run our main_8080.py script directly
        main_process = subprocess.Popen(
            ["python", "main_8080.py"], 
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Log output from the process
        def log_output():
            # Only try to read output if we have a valid process with stdout
            if main_process and main_process.stdout:
                try:
                    for line in iter(main_process.stdout.readline, ''):
                        if line:
                            logger.info(f"[SERVER] {line.strip()}")
                except Exception as e:
                    logger.error(f"Error reading process output: {e}")
        
        # Check if process is still running
        while main_process and main_process.poll() is None:
            log_output()
            time.sleep(0.1)
            
        # If we get here, the process has exited
        return_code = main_process.returncode
        logger.error(f"Server process exited unexpectedly with code {return_code}")
        return False
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return False

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Make sure we cleanup on exit
    import atexit
    atexit.register(cleanup)
    
    try:
        # Start the server and wait for it to finish
        success = start_server()
        if not success:
            logger.error("Server failed to start or crashed. Exiting.")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        cleanup()

if __name__ == "__main__":
    main()
