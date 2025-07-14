#!/usr/bin/env python3
"""
Port 8080 Adapter for SmartDispute.ai

This script creates a simple HTTP server on port 8080 that redirects requests
to port 5000 where the main Flask application is running.
"""
import os
import sys
import http.server
import socketserver
import logging
import signal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests by redirecting to the main application on port 5000
        """
        try:
            target_host = self.headers.get("Host", "").split(":")[0]
            redirect_url = f"http://{target_host}:5000{self.path}"
            
            self.send_response(302)  # Found/Redirect
            self.send_header('Location', redirect_url)
            self.end_headers()
            logger.info(f"Redirecting GET request from {self.path} to {redirect_url}")
        except Exception as e:
            logger.error(f"Error in do_GET: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
    
    def do_POST(self):
        """
        Handle POST requests by redirecting to the main application on port 5000
        """
        try:
            target_host = self.headers.get("Host", "").split(":")[0]
            redirect_url = f"http://{target_host}:5000{self.path}"
            
            self.send_response(307)  # Temporary Redirect (preserves method and body)
            self.send_header('Location', redirect_url)
            self.end_headers()
            logger.info(f"Redirecting POST request from {self.path} to {redirect_url}")
        except Exception as e:
            logger.error(f"Error in do_POST: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
    
    def log_message(self, format, *args):
        """
        Override the default log_message method to use our logger
        """
        logger.debug(f"{self.client_address[0]} - {format % args}")

class ReuseAddressTCPServer(socketserver.TCPServer):
    """
    TCP Server that allows address reuse to avoid 'Address already in use' errors
    """
    allow_reuse_address = True

def signal_handler(sig, frame):
    """
    Handle signals to properly clean up
    """
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)

def main():
    """
    Main function to run the HTTP server on port 8080
    """
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start the HTTP server
    try:
        with ReuseAddressTCPServer(("", 8080), RedirectHandler) as httpd:
            logger.info("Starting HTTP server on port 8080...")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting HTTP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
