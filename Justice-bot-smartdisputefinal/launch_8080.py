#!/usr/bin/env python3
"""
SmartDispute.ai Launcher
This script runs both the main application on port 5000 and a port 8080 server
"""

import subprocess
import os
import sys
import signal
import time
import logging
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global process variables
main_process = None
port8080_process = None

def clean_exit(status=0):
    """Clean up resources and exit"""
    global main_process, port8080_process
    
    # Kill any existing processes
    if main_process:
        try:
            logging.info("Terminating main application process")
            main_process.terminate()
            main_process.wait(timeout=5)
        except Exception as e:
            logging.error(f"Error terminating main process: {e}")
            try:
                main_process.kill()
            except:
                pass
    
    if port8080_process:
        try:
            logging.info("Terminating port 8080 process")
            port8080_process.terminate()
            port8080_process.wait(timeout=5)
        except Exception as e:
            logging.error(f"Error terminating port 8080 process: {e}")
            try:
                port8080_process.kill()
            except:
                pass
    
    sys.exit(status)

def signal_handler(sig, frame):
    """Handle termination signals"""
    logging.info(f"Received signal {sig}, shutting down")
    clean_exit(0)

def monitor_process(process, name):
    """Monitor a subprocess and log its output"""
    for line in iter(process.stdout.readline, b''):
        logging.info(f"{name}: {line.decode('utf-8').rstrip()}")
    
    # If we get here, the process has ended
    return_code = process.poll()
    logging.info(f"{name} process exited with code {return_code}")
    
    if name == "Main" and return_code != 0:
        logging.error("Main application failed, shutting down")
        clean_exit(1)

def start_main_app():
    """Start the main application on port 5000"""
    global main_process
    
    logging.info("Starting main application on port 5000")
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "2",
        "--timeout", "120",
        "--reload",
        "main:app"
    ]
    
    try:
        main_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False
        )
        
        # Start output monitor in a thread
        monitor_thread = threading.Thread(
            target=monitor_process,
            args=(main_process, "Main"),
            daemon=True
        )
        monitor_thread.start()
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running
        if main_process.poll() is not None:
            logging.error(f"Main application failed to start, exit code: {main_process.returncode}")
            clean_exit(1)
        
        logging.info("Main application started successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error starting main application: {e}")
        return False

def start_port8080_server():
    """Start the port 8080 server"""
    global port8080_process
    
    logging.info("Starting port 8080 server")
    
    # Wait for the main app to be ready
    time.sleep(5)
    
    cmd = [
        "python3",
        "direct_port8080.py"
    ]
    
    try:
        port8080_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=False
        )
        
        # Start output monitor in a thread
        monitor_thread = threading.Thread(
            target=monitor_process,
            args=(port8080_process, "Port8080"),
            daemon=True
        )
        monitor_thread.start()
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running
        if port8080_process.poll() is not None:
            logging.error(f"Port 8080 server failed to start, exit code: {port8080_process.returncode}")
            return False
        
        logging.info("Port 8080 server started successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error starting port 8080 server: {e}")
        return False

def main():
    """Main function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print environment information
    logging.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
    logging.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not found')}")
    logging.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not found')}")
    
    # Start main application
    if not start_main_app():
        logging.error("Failed to start main application, exiting")
        clean_exit(1)
    
    # Start port 8080 server
    if not start_port8080_server():
        logging.error("Failed to start port 8080 server, exiting")
        clean_exit(1)
    
    # Keep the script running
    try:
        while True:
            # Check if processes are still running
            if main_process.poll() is not None:
                logging.error("Main application unexpectedly exited")
                clean_exit(1)
            
            if port8080_process.poll() is not None:
                logging.warning("Port 8080 server unexpectedly exited, restarting")
                if not start_port8080_server():
                    logging.error("Failed to restart port 8080 server, exiting")
                    clean_exit(1)
            
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
        clean_exit(0)

if __name__ == "__main__":
    main()