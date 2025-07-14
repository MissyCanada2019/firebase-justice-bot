#!/usr/bin/env python3
"""
Simple Port 8080 to 5000 Forwarder for SmartDispute.ai
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ForwardingHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP handler that forwards all requests to port 5000"""
    
    def do_GET(self):
        self._forward_request()
    
    def do_POST(self):
        self._forward_request()
    
    def do_PUT(self):
        self._forward_request()
    
    def do_DELETE(self):
        self._forward_request()
    
    def _forward_request(self):
        """Forward request to port 5000"""
        try:
            # Build target URL
            url = f"http://127.0.0.1:5000{self.path}"
            
            # Get request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request
            req = urllib.request.Request(url, data=body)
            
            # Copy headers (excluding problematic ones)
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    req.add_header(header, value)
            
            # Make request to main app
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    # Send response
                    self.send_response(response.getcode())
                    
                    # Copy response headers
                    for header, value in response.headers.items():
                        if header.lower() not in ['connection', 'transfer-encoding']:
                            self.send_header(header, value)
                    self.end_headers()
                    
                    # Copy response body
                    self.wfile.write(response.read())
                    
            except urllib.error.URLError:
                # Main app not available
                self.send_error(502, "Main application not available")
                
        except Exception as e:
            logger.error(f"Forwarding error: {e}")
            self.send_error(500, "Internal server error")
    
    def log_message(self, format, *args):
        """Log requests"""
        logger.info(f"8080->5000: {format % args}")

def main():
    """Start the port forwarder"""
    try:
        with socketserver.TCPServer(("0.0.0.0", 8080), ForwardingHandler) as httpd:
            logger.info("Port forwarder running on port 8080, forwarding to port 5000")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error("Port 8080 is already in use")
        else:
            logger.error(f"Failed to start server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down port forwarder")

if __name__ == "__main__":
    main()