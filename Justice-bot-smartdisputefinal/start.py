#!/usr/bin/env python3
"""
Ultra-simple script for starting SmartDispute.ai in Replit
This uses the most minimal possible server to respond to port checks
"""
import os
import socket
import threading
import time
import subprocess
import sys

# Configuration
PORT = 5000
MAIN_APP_COMMAND = ["gunicorn", "--bind", f"0.0.0.0:{PORT}", "main:app"]
MAX_RETRIES = 10  # Maximum number of port-binding retries

def log(message):
    """Log a message with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

def check_port_available():
    """Check if the port is available"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', PORT))
        return True
    except OSError:
        return False
    finally:
        s.close()

# Create a bare minimum socket server
def minimal_server():
    """Create a minimal socket server that responds immediately"""
    # Make sure port is available
    for attempt in range(1, MAX_RETRIES + 1):
        if check_port_available():
            break
        log(f"Port {PORT} not available. Attempt {attempt}/{MAX_RETRIES}...")
        time.sleep(1)
    else:
        log(f"ERROR: Could not bind to port {PORT} after {MAX_RETRIES} attempts.")
        sys.exit(1)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.settimeout(0.5)  # Short timeout to allow checking of shutdown flag
        server_socket.listen(5)
        log(f"Minimal server started on port {PORT}")
        
        # Continue accepting connections until shutdown
        while True:
            try:
                conn, addr = server_socket.accept()
                with conn:
                    log(f"Connection from {addr} - sending 'Service is starting' response")
                    # Send a minimal HTTP response
                    response = b"HTTP/1.1 200 OK\r\n"
                    response += b"Content-Type: text/html\r\n"
                    response += b"Connection: close\r\n"
                    response += b"\r\n"
                    response += b"<html><body><h1>SmartDispute.ai is starting...</h1><p>Please wait a moment for the application to initialize.</p></body></html>"
                    conn.send(response)
            except socket.timeout:
                # This allows us to check the shutdown flag regularly
                continue
            except Exception as e:
                log(f"Error handling connection: {e}")
    
    except Exception as e:
        log(f"Error in minimal server: {e}")
    
    finally:
        server_socket.close()
        log("Minimal server stopped")

# Start the actual application
def start_app():
    """Start the real application after a short delay"""
    # Wait briefly to make sure minimal server has started
    time.sleep(2)
    
    log(f"Starting main application: {' '.join(MAIN_APP_COMMAND)}")
    
    # Start the main application
    try:
        os.execvp(MAIN_APP_COMMAND[0], MAIN_APP_COMMAND)
    except Exception as e:
        log(f"Failed to start main application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    log("SmartDispute.ai Rapid Starter")
    log("--------------------------")
    
    # Start the minimal server in a separate thread
    minimal_thread = threading.Thread(target=minimal_server)
    minimal_thread.daemon = True
    minimal_thread.start()
    
    # Start the app in the main thread
    start_app()
    
    # We should never reach this point as start_app() replaces this process
    log("ERROR: Main application failed to start")
    sys.exit(1)