#!/usr/bin/env python3
"""
Port 8080 Server for Replit Web Access
Simple HTTP server that redirects to the main application
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Port8080Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward_request()
    
    def do_POST(self):
        self.forward_request()
    
    def forward_request(self):
        try:
            # Forward to main app on port 5000
            target_url = f"http://127.0.0.1:5000{self.path}"
            
            # Handle request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request
            req = urllib.request.Request(target_url, data=body)
            
            # Copy headers
            for name, value in self.headers.items():
                if name.lower() not in ['host', 'connection']:
                    req.add_header(name, value)
            
            # Make request
            try:
                response = urllib.request.urlopen(req, timeout=10)
                
                # Send response
                self.send_response(response.getcode())
                
                # Copy headers
                for name, value in response.headers.items():
                    if name.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(name, value)
                self.end_headers()
                
                # Copy body
                self.wfile.write(response.read())
                
            except urllib.error.URLError:
                self.send_error(502, "Main application not available")
                
        except Exception as e:
            logger.error(f"Error: {e}")
            self.send_error(500, "Server error")
    
    def log_message(self, format, *args):
        logger.info(f"Port 8080: {format % args}")

def main():
    try:
        with socketserver.TCPServer(("0.0.0.0", 8080), Port8080Handler) as httpd:
            logger.info("Port 8080 server started - forwarding to port 5000")
            httpd.serve_forever()
    except OSError as e:
        logger.error(f"Port 8080 already in use: {e}")
    except KeyboardInterrupt:
        logger.info("Server stopped")

if __name__ == "__main__":
    main()