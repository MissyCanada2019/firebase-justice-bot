#!/usr/bin/env python3
"""
Ultra Simple Port Adapter for SmartDispute.ai

This script creates a basic HTTP server on port 8080 that
forwards all requests to the main application on port 5000.
It's designed to be as simple and reliable as possible.
"""
import sys
import os
import time
import http.server
import socketserver
import threading
import urllib.request
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simple_adapter.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

# Configuration
PORT = 8080
TARGET = "http://localhost:5000"

class SimpleProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.proxy_request("GET")
        
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        self.proxy_request("POST", post_data)
    
    def proxy_request(self, method, body=None):
        """Forward the request to the target server"""
        target_url = TARGET + self.path
        logger.info(f"Forwarding {method} request to {target_url}")
        
        # Create request object
        req = urllib.request.Request(
            url=target_url,
            data=body,
            method=method
        )
        
        # Copy headers
        for header in self.headers:
            if header.lower() != 'host':
                req.add_header(header, self.headers[header])
                
        try:
            # Send the request to the target server
            with urllib.request.urlopen(req) as response:
                # Copy the response status
                self.send_response(response.status)
                
                # Copy the response headers
                for header in response.headers:
                    self.send_header(header, response.headers[header])
                self.end_headers()
                
                # Copy the response content
                self.wfile.write(response.read())
                
        except Exception as e:
            logger.error(f"Error forwarding request: {e}")
            self.send_response(502)  # Bad Gateway
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.client_address[0]} - {format % args}")

def run_server():
    """Run the HTTP server"""
    try:
        with socketserver.TCPServer(("", PORT), SimpleProxyHandler) as httpd:
            logger.info(f"=== SmartDispute.ai Simple Port Adapter ===")
            logger.info(f"Server started on port {PORT}")
            logger.info(f"Forwarding to {TARGET}")
            
            # Save PID to file
            with open('simple_adapter.pid', 'w') as f:
                f.write(str(os.getpid()))
                
            # Serve until interrupted
            httpd.serve_forever()
            
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(run_server())