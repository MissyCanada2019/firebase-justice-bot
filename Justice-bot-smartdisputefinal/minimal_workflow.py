"""
Minimal workflow script for running a basic Flask application
This is a diagnostic tool to test if the server has basic connectivity
"""
import subprocess
import sys
import signal
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup():
    """Clean up on exit"""
    logger.info("Cleaning up...")

def signal_handler(sig, frame):
    """Handle signals to properly clean up"""
    logger.info(f"Received signal {sig}")
    cleanup()
    sys.exit(0)

def run_minimal_app():
    """Run the minimal Flask app directly"""
    logger.info("Starting minimal Flask application...")
    
    try:
        # Using gunicorn for better reliability
        cmd = [
            "gunicorn",
            "--bind", "0.0.0.0:5000",
            "--access-logfile", "-",  # Log to stdout
            "--error-logfile", "-",   # Log errors to stdout
            "--log-level", "info",
            "absolutely_minimal:app"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep the main thread alive while the subprocess runs
        logger.info(f"Minimal app started with PID {process.pid}")
        process.wait()
        
    except Exception as e:
        logger.error(f"Error running minimal app: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    run_minimal_app()
