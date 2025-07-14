#!/usr/bin/env python3
"""
Enhanced HTTP Server for port 8080 - Direct Redirect Version
Improved version with simplified direct redirection logic
"""

import http.server
import socketserver
import os
import sys
import time
import socket
import urllib.parse

# Configuration
PORT = 8080
MAIN_APP_PORT = 5000
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN", os.environ.get("REPLIT_DOMAINS", ""))
if "," in REPLIT_DOMAIN:  # Handle multiple domains
    REPLIT_DOMAIN = REPLIT_DOMAIN.split(",")[0].strip()

class DirectRedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests by redirecting to the Replit domain
        """
        # For health check, return success directly
        if self.path == "/health" or self.path == "/health-check":
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            return
            
        self.send_response(302)  # Found/Redirect
        if REPLIT_DOMAIN:
            # Use the Replit domain directly
            target = f"https://{REPLIT_DOMAIN}{self.path}"
            print(f"Redirecting to: {target}")
            self.send_header('Location', target)
        else:
            # Fallback to localhost on port 5000
            self.send_header('Location', f'http://localhost:{MAIN_APP_PORT}{self.path}')
        self.end_headers()
    
    def do_POST(self):
        """
        Handle POST requests with redirect
        """
        self.do_GET()  # Just redirect POST requests too
    
    def log_message(self, format, *args):
        """
        Log messages to stdout
        """
        sys.stdout.write(f"{self.client_address[0]} - {format % args}\n")
        sys.stdout.flush()

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_main_app(max_attempts=30, interval=2):
    """Wait for the main app to start"""
    print(f"Waiting for main app on port {MAIN_APP_PORT}...")
    for i in range(max_attempts):
        if is_port_in_use(MAIN_APP_PORT):
            print(f"Main app is running on port {MAIN_APP_PORT}")
            return True
        print(f"Attempt {i+1}/{max_attempts}: Main app not yet available")
        time.sleep(interval)
    print(f"Main app not available after {max_attempts} attempts")
    return False

def main():
    """
    Run the server
    """
    print(f"Enhanced Port 8080 Server")
    print(f"Replit domain: {REPLIT_DOMAIN or 'Not found'}")
    
    # Wait for main app to be available
    wait_for_main_app()
    
    try:
        # Create and start the server
        server = socketserver.TCPServer(("0.0.0.0", PORT), DirectRedirectHandler)
        print(f"Starting server on port {PORT}")
        print(f"Redirect target: https://{REPLIT_DOMAIN}/")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()