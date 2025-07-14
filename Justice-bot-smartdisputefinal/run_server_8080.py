#!/usr/bin/env python3
"""
Production-ready server for SmartDispute.ai on port 8080
This is specifically for Replit compatibility
"""

import os
import sys
import signal
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    logging.info("Received signal to shutdown")
    sys.exit(0)

def main():
    """Main function to run the server"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print environment information
    logging.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
    logging.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not found')}")
    logging.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not found')}")
    
    # Configure Gunicorn command
    gunicorn_cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:8080",  # Bind to port 8080 specifically
        "--workers", "2",
        "--timeout", "120",
        "--log-level", "info",
        "--access-logfile", "-",  # Log to stdout
        "--error-logfile", "-",  # Log to stderr
        "--reload",              # Auto-reload on code changes
        "main:app"              # Use main:app as the WSGI application
    ]
    
    logging.info(f"Starting server with command: {' '.join(gunicorn_cmd)}")
    
    # Start Gunicorn
    try:
        process = subprocess.run(
            gunicorn_cmd,
            check=True
        )
        return process.returncode
    except subprocess.CalledProcessError as e:
        logging.error(f"Server failed with exit code {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        return 0
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())