#!/usr/bin/env python3
"""
Simple port 8080 listener for SmartDispute.ai

This script creates a simple HTTP server that listens on port 8080
and redirects all traffic to the main application running on port 5000.
"""
import http.server
import socketserver
import urllib.request
import urllib.error
import sys
import os
import time

LISTEN_PORT = 8080
MAIN_APP_PORT = 5000
MAIN_APP_URL = f"http://localhost:{MAIN_APP_PORT}"

MAX_RETRIES = 30
RETRY_INTERVAL = 1  # seconds

class SimpleProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests by forwarding to the main app"""
        try:
            # Forward the request to the main app
            target_url = f"{MAIN_APP_URL}{self.path}"
            response = urllib.request.urlopen(target_url)
            
            # Set the same status code
            self.send_response(response.status)
            
            # Copy all headers
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()
            
            # Copy the response body
            self.wfile.write(response.read())
            
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"Error forwarding request: {str(e)}".encode())
    
    def do_POST(self):
        """Handle POST requests by forwarding to the main app"""
        try:
            # Get the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Forward the request to the main app
            target_url = f"{MAIN_APP_URL}{self.path}"
            headers = {key: val for key, val in self.headers.items()}
            
            request = urllib.request.Request(
                target_url, 
                data=post_data,
                headers=headers,
                method='POST'
            )
            
            response = urllib.request.urlopen(request)
            
            # Set the same status code
            self.send_response(response.status)
            
            # Copy all headers
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()
            
            # Copy the response body
            self.wfile.write(response.read())
            
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"Error forwarding request: {str(e)}".encode())
    
    def log_message(self, format, *args):
        """Custom logging function"""
        sys.stderr.write(f"Port 8080 Proxy: {self.client_address[0]} - {format % args}\n")

def is_port_in_use(port):
    """Check if a port is already in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_main_app():
    """Wait for the main app to be ready"""
    print(f"Waiting for main app to be available on port {MAIN_APP_PORT}...")
    for i in range(MAX_RETRIES):
        if is_port_in_use(MAIN_APP_PORT):
            print(f"Main app is available on port {MAIN_APP_PORT}")
            return True
        print(f"Retry {i+1}/{MAX_RETRIES}...")
        time.sleep(RETRY_INTERVAL)
    
    print(f"Main app not available on port {MAIN_APP_PORT} after {MAX_RETRIES} retries")
    return False

def main():
    """Main function"""
    # Check if port 8080 is already in use
    if is_port_in_use(LISTEN_PORT):
        print(f"Port {LISTEN_PORT} is already in use. Stopping...")
        return 1
    
    # Wait for the main app to be ready
    if not wait_for_main_app():
        return 1
    
    # Create the server
    handler = SimpleProxyHandler
    httpd = socketserver.TCPServer(("0.0.0.0", LISTEN_PORT), handler)
    
    print(f"Starting proxy server on port {LISTEN_PORT}")
    print(f"Forwarding requests to {MAIN_APP_URL}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        httpd.server_close()
        print("Server stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
