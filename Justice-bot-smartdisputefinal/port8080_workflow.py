#!/usr/bin/env python3
"""
Port 8080 Workflow for SmartDispute.ai

This script provides a workflow that runs the application on port 8080
as required by Replit for web access.
"""

import os
import sys
import time
import signal
import subprocess
import atexit

# Path to the main application file that will run on port 8080
MAIN_APP_PATH = "main_8080.py"

# Flag to control the main loop
running = True

def signal_handler(sig, frame):
    """Handle signals for graceful shutdown"""
    global running
    print(f"\nReceived signal {sig}, shutting down...")
    running = False

def cleanup():
    """Clean up resources on exit"""
    print("Cleaning up resources...")
    # Perform any necessary cleanup here

def is_port_in_use(port):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_app_on_port_8080():
    """Start the application on port 8080"""
    try:
        # Make sure the main app file exists
        if not os.path.exists(MAIN_APP_PATH):
            print(f"Error: {MAIN_APP_PATH} not found!")
            return None
        
        # If port 8080 is already in use, don't start a new instance
        if is_port_in_use(8080):
            print("Port 8080 is already in use. Not starting a new instance.")
            return None
        
        print(f"Starting application on port 8080 using {MAIN_APP_PATH}...")
        
        # Use Python to run the app
        process = subprocess.Popen(
            [sys.executable, MAIN_APP_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1  # Line buffered
        )
        
        # Log the process ID
        print(f"Started process with PID: {process.pid}")
        
        return process
    except Exception as e:
        print(f"Error starting application: {e}")
        return None

def log_output(process):
    """Log output from the process"""
    if process and process.stdout:
        line = process.stdout.readline()
        if line:
            sys.stdout.write(f"[Port 8080] {line}")
            sys.stdout.flush()
            return True
    return False

def main():
    """Main function to run the workflow"""
    global running
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function to run on exit
    atexit.register(cleanup)
    
    print("Starting Port 8080 Workflow for SmartDispute.ai")
    
    # Start the application on port 8080
    app_process = start_app_on_port_8080()
    
    # Wait for the application to bind to port 8080
    retry_count = 0
    max_retries = 10
    while not is_port_in_use(8080) and retry_count < max_retries:
        time.sleep(1)
        retry_count += 1
        print(f"Waiting for application to bind to port 8080... ({retry_count}/{max_retries})")
    
    if retry_count >= max_retries and not is_port_in_use(8080):
        print("Error: Application failed to bind to port 8080.")
        if app_process:
            app_process.terminate()
        sys.exit(1)
    
    print("Application is running on port 8080.")
    
    # Main loop to keep the workflow running and handle application output
    while running:
        if app_process:
            # Log any output from the process
            if not log_output(app_process):
                # If there's no output, sleep briefly to avoid busy waiting
                time.sleep(0.1)
            
            # Check if the process is still running
            if app_process.poll() is not None:
                # Process has exited
                print(f"Application process exited with code: {app_process.returncode}")
                # Restart the application
                print("Restarting application...")
                app_process = start_app_on_port_8080()
        else:
            # No process running, try to start one
            app_process = start_app_on_port_8080()
            if not app_process:
                # Failed to start, wait before trying again
                time.sleep(5)
    
    # Terminate the application process if it's still running
    if app_process and app_process.poll() is None:
        print("Terminating application process...")
        app_process.terminate()
        # Wait for the process to terminate
        app_process.wait(timeout=5)
    
    print("Port 8080 Workflow has been shut down.")

if __name__ == "__main__":
    main()
