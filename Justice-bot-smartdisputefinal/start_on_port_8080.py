"""
Production-ready port 8080 server for SmartDispute.ai
This script runs the application on port 8080 using gunicorn
"""
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """
    Run the application on port 8080 using gunicorn
    """
    # Stop any existing workflows first
    try:
        subprocess.run(["pkill", "-f", "gunicorn"], check=False)
        logging.info("Stopped existing gunicorn processes")
    except Exception as e:
        logging.warning(f"Could not stop existing processes: {e}")
    
    # Start gunicorn directly on port 8080
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:8080",
        "--reuse-port",
        "--reload",
        "app:app"
    ]
    
    logging.info(f"Starting gunicorn on port 8080 with command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()