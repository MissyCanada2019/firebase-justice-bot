#!/usr/bin/env python3
"""
Port 8080 Forwarder for SmartDispute.ai
This creates a simple HTTP server on port 8080 that forwards all requests to the main application on port 5000
"""
import http.server
import socketserver
import urllib.request
import urllib.parse
import logging
import sys
import os
from urllib.error import URLError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
FORWARD_HOST = "127.0.0.1"
FORWARD_PORT = 5000
LISTEN_PORT = 8080

class ForwardingHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward_request()
    
    def do_POST(self):
        self.forward_request()
    
    def do_PUT(self):
        self.forward_request()
    
    def do_DELETE(self):
        self.forward_request()
    
    def forward_request(self):
        try:
            # Build the target URL
            target_url = f"http://{FORWARD_HOST}:{FORWARD_PORT}{self.path}"
            
            # Prepare headers
            headers = {}
            for key, value in self.headers.items():
                if key.lower() not in ['host', 'connection']:
                    headers[key] = value
            
            # Handle request body for POST/PUT
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create the request
            req = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
            
            # Forward the request
            with urllib.request.urlopen(req, timeout=30) as response:
                # Send response status
                self.send_response(response.status)
                
                # Forward response headers
                for key, value in response.headers.items():
                    if key.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(key, value)
                self.end_headers()
                
                # Forward response body
                self.wfile.write(response.read())
                
        except URLError as e:
            logger.error(f"Failed to forward request to {target_url}: {e}")
            # Send a helpful error page
            self.send_response(503)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            error_page = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>SmartDispute.ai - Service Starting</title>
                <meta http-equiv="refresh" content="5">
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: #e74c3c; }}
                    .info {{ color: #3498db; }}
                </style>
            </head>
            <body>
                <h1>SmartDispute.ai</h1>
                <p class="info">Main application is starting up...</p>
                <p>This page will automatically refresh in 5 seconds.</p>
                <p class="error">If this persists, the main application on port {FORWARD_PORT} may not be running.</p>
                <hr>
                <small>Port 8080 Forwarder - Error: {str(e)}</small>
            </body>
            </html>
            """
            self.wfile.write(error_page.encode())
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Internal Server Error: {str(e)}".encode())
    
    def log_message(self, format, *args):
        # Log requests
        logger.info(f"[8080->5000] {format % args}")

def main():
    logger.info(f"Starting port forwarder on port {LISTEN_PORT}")
    logger.info(f"Forwarding requests to {FORWARD_HOST}:{FORWARD_PORT}")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", LISTEN_PORT), ForwardingHandler) as httpd:
            logger.info(f"Port forwarder serving on port {LISTEN_PORT}")
            logger.info("Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Port forwarder stopped by user")
    except Exception as e:
        logger.error(f"Failed to start port forwarder: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()