#!/usr/bin/env python3
# Port 8080 Adapter Workflow for SmartDispute.ai

import http.server
import socketserver
import os
import sys
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
LISTEN_PORT = 8080
MAIN_APP_PORT = 5000

class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)  # Redirect
        # Replace the port in the Host header
        new_location = f"http://localhost:{MAIN_APP_PORT}{self.path}"
        self.send_header('Location', new_location)
        self.end_headers()
    
    def do_POST(self):
        self.send_response(302)  # Redirect
        new_location = f"http://localhost:{MAIN_APP_PORT}{self.path}"
        self.send_header('Location', new_location)
        self.end_headers()
    
    def log_message(self, format, *args):
        logging.info(f"{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}")

def start_server():
    """Start the HTTP server"""
    with socketserver.TCPServer(("", LISTEN_PORT), RedirectHandler) as httpd:
        print(f"Port {LISTEN_PORT} adapter started - redirecting to port {MAIN_APP_PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    print("===== SmartDispute.ai Port 8080 Adapter Workflow =====")
    print(f"Starting adapter to redirect port {LISTEN_PORT} -> {MAIN_APP_PORT}")
    
    # Wait for the main application to start
    print("Waiting for main application to start...")
    time.sleep(5)
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nShutdown requested... exiting")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)