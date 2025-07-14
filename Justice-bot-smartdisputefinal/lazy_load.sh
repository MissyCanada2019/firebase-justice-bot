#!/bin/bash
# This is an optimized startup script for SmartDispute.ai
# It binds to port 5000 quickly, then initializes the app in the background

# Start a temporary HTTP server to respond to Replit's port check
python -c '
import http.server
import threading
import time
import os
import socket
import subprocess

def is_port_in_use(port):
    """Check if a port is already in use"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        s.bind(("0.0.0.0", port))
    except socket.error:
        result = True
    s.close()
    return result

# Check if port is already in use
if is_port_in_use(5000):
    print("Port 5000 is already in use! Exiting.")
    exit(1)

# Simple HTTP request handler to respond to Replit port check
class QuickHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"SmartDispute.ai is starting... Please wait.")
    
    # Make the handler quiet by suppressing log messages
    def log_message(self, format, *args):
        return

# Start the main app in a separate thread
def start_main_app():
    print("Starting main app in the background...")
    time.sleep(1.5)  # Give the quick server time to respond to Replit port check
    
    # Replace this process with the actual app using gunicorn
    os.execvp("gunicorn", [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--timeout", "120",
        "main:app"
    ])

# Start the main app thread
thread = threading.Thread(target=start_main_app)
thread.daemon = True
thread.start()

# Start a simple HTTP server that responds immediately
print("Starting quick HTTP server on port 5000...")
quick_server = http.server.HTTPServer(("0.0.0.0", 5000), QuickHandler)
quick_server.handle_request()  # Handle just one request (from Replit port check)
print("Quick server has responded, waiting for main app to start...")

# Wait for the main app thread to finish (it won\'t)
thread.join()
'