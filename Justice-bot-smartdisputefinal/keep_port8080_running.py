#!/usr/bin/env python3
"""
Auto-restart script for port 8080 HTTP server
This script monitors the HTTP server on port 8080 and restarts it if it crashes
"""
import subprocess
import time
import os
import socket
import sys
import signal

# Constants
CHECK_INTERVAL = 10  # Check every 10 seconds
HTTP_SERVER_SCRIPT = "simple_http_server.py"
PID_FILE = "http_server.pid"
LOG_FILE = "http_server.log"

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def is_process_running(pid):
    """Check if a process with the given PID is running"""
    try:
        os.kill(pid, 0)  # Signal 0 doesn't kill the process but checks if it exists
        return True
    except OSError:
        return False

def get_server_pid():
    """Get the PID of the HTTP server from the PID file"""
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
                return pid
        return None
    except:
        return None

def start_server():
    """Start the HTTP server and return its PID"""
    try:
        # Run the server in the background
        process = subprocess.Popen(
            [sys.executable, HTTP_SERVER_SCRIPT],
            stdout=open(LOG_FILE, 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # Save the PID to file
        pid = process.pid
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
        
        print(f"Started HTTP server with PID {pid}")
        return pid
    except Exception as e:
        print(f"Error starting server: {e}")
        return None

def stop_server(pid):
    """Stop the HTTP server with the given PID"""
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Stopped HTTP server with PID {pid}")
        except OSError:
            print(f"Process {pid} already terminated")

def cleanup():
    """Clean up resources on exit"""
    pid = get_server_pid()
    if pid:
        stop_server(pid)
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def main():
    """Main function"""
    print("Starting port 8080 monitor")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))
    
    # Register cleanup function
    atexit.register(cleanup)
    
    try:
        while True:
            # Check if port 8080 is in use
            if not is_port_in_use(8080):
                print("Port 8080 is not in use, starting HTTP server...")
                
                # Check if we have a PID file
                old_pid = get_server_pid()
                if old_pid and is_process_running(old_pid):
                    print(f"Server process {old_pid} is still running but port is not in use")
                    stop_server(old_pid)
                
                # Start a new server
                start_server()
            else:
                # Port is in use, check if it's our server
                pid = get_server_pid()
                if pid and not is_process_running(pid):
                    print(f"Server process {pid} has died but port is in use by another process")
                    # Clean up the PID file
                    if os.path.exists(PID_FILE):
                        os.remove(PID_FILE)
            
            # Wait for the next check
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        cleanup()

if __name__ == "__main__":
    import atexit
    main()