#!/usr/bin/env python3
"""
Auto Port Adapter for SmartDispute.ai

This script runs in the background and automatically starts the port 8080 adapter
whenever the main application is running on port 5000.

It periodically checks if the main app is running and ensures port 8080 access is available.
This allows the application to be accessed via Replit's web interface, which seems to favor port 8080.
"""

import os
import time
import socket
import subprocess
import signal
import sys
import atexit

# Configuration
MAIN_PORT = 5000
ADAPTER_PORT = 8080
CHECK_INTERVAL = 5  # seconds

# Global variables
adapter_process = None
running = True

def is_port_in_use(port):
    """Check if a port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False

def start_port_adapter():
    """Start the port adapter server process"""
    global adapter_process
    
    # Check if adapter is already running
    if adapter_process and adapter_process.poll() is None:
        print("Port adapter already running")
        return
    
    try:
        print(f"Starting port adapter on port {ADAPTER_PORT}...")
        # Use port8080.py as the adapter
        adapter_process = subprocess.Popen(
            ["python", "port8080.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Save process ID to file
        with open('port_adapter.pid', 'w') as f:
            f.write(str(os.getpid()))
            
        print(f"Port adapter started with PID {adapter_process.pid}")
    except Exception as e:
        print(f"Failed to start port adapter: {e}")

def stop_port_adapter():
    """Stop the port adapter server process"""
    global adapter_process
    
    if adapter_process and adapter_process.poll() is None:
        try:
            print(f"Stopping port adapter (PID: {adapter_process.pid})")
            adapter_process.terminate()
            try:
                adapter_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                adapter_process.kill()
            
            print("Port adapter stopped")
        except Exception as e:
            print(f"Error stopping port adapter: {e}")
        
        adapter_process = None

def check_and_update():
    """Check if main app is running and start/stop port adapter as needed"""
    main_running = is_port_in_use(MAIN_PORT)
    adapter_running = adapter_process and adapter_process.poll() is None
    
    if main_running and not adapter_running:
        # Main app is running but adapter is not - start it
        print("Main application is running, starting port adapter")
        start_port_adapter()
    elif not main_running and adapter_running:
        # Main app is not running but adapter is - stop it
        print("Main application is not running, stopping port adapter")
        stop_port_adapter()
    elif main_running and adapter_running:
        # Both are running - check if adapter is responsive
        if not is_port_in_use(ADAPTER_PORT):
            print("Port adapter is not responding, restarting")
            stop_port_adapter()
            start_port_adapter()

def main_loop():
    """Main loop that periodically checks and updates"""
    while running:
        try:
            check_and_update()
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Error in main loop: {e}")
            # Continue running despite errors
            time.sleep(CHECK_INTERVAL)

def signal_handler(sig, frame):
    """Handle signals to properly clean up"""
    global running
    print(f"Received signal {sig}, shutting down...")
    running = False
    stop_port_adapter()
    
    # Remove PID file
    try:
        os.remove('port_adapter.pid')
    except:
        pass
    
    sys.exit(0)

def cleanup():
    """Clean up function for atexit"""
    global running
    if running:
        running = False
        stop_port_adapter()
        
        # Remove PID file
        try:
            os.remove('port_adapter.pid')
        except:
            pass

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function
    atexit.register(cleanup)
    
    print("Starting SmartDispute.ai Auto Port Adapter")
    print(f"Monitoring main app on port {MAIN_PORT} and managing adapter on port {ADAPTER_PORT}")
    
    # Save PID to file
    with open('port_adapter.pid', 'w') as f:
        f.write(str(os.getpid()))
    
    # Run the main loop
    main_loop()