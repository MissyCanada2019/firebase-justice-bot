"""Single port workflow for SmartDispute.ai"""
import os
import sys
import subprocess
import time
import signal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def cleanup():
    """Clean up on exit"""
    logging.info("Cleaning up...")

def signal_handler(sig, frame):
    """Handle signals to properly clean up"""
    logging.info(f"Received signal {sig}")
    cleanup()
    sys.exit(0)

def main():
    """Start single port application"""
    logging.info("Starting SmartDispute.ai on port 5000 only...")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get path to gunicorn
    gunicorn_path = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'bin', 'gunicorn')
    if not os.path.exists(gunicorn_path):
        gunicorn_path = 'gunicorn'  # Use system-wide gunicorn
    
    try:
        # Start the application with gunicorn
        cmd = [
            gunicorn_path,
            "--bind", "0.0.0.0:5000",
            "--reuse-port",
            "--reload",
            "main:app"
        ]
        
        logging.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        
        # Keep the process running
        logging.info(f"Gunicorn started with PID {process.pid}")
        process.wait()
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    except Exception as e:
        logging.error(f"Error starting server: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
