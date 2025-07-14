#!/usr/bin/env python3
"""
Simple HTTP Port Forwarder for SmartDispute.ai
Forwards port 8080 requests to the main application on port 5000
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import logging
import threading
import time
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler that forwards requests to port 5000"""
    
    def do_GET(self):
        """Handle GET requests by forwarding to port 5000"""
        self.forward_request('GET')
    
    def do_POST(self):
        """Handle POST requests by forwarding to port 5000"""
        self.forward_request('POST')
    
    def do_PUT(self):
        """Handle PUT requests by forwarding to port 5000"""
        self.forward_request('PUT')
    
    def do_DELETE(self):
        """Handle DELETE requests by forwarding to port 5000"""
        self.forward_request('DELETE')
    
    def forward_request(self, method):
        """Forward request to the main application on port 5000"""
        try:
            # Build the target URL
            target_url = f"http://127.0.0.1:5000{self.path}"
            
            # Prepare headers
            headers = {}
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    headers[header] = value
            
            # Handle request body for POST/PUT requests
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create the request
            req = urllib.request.Request(target_url, data=request_body, headers=headers, method=method)
            
            # Forward the request
            with urllib.request.urlopen(req, timeout=30) as response:
                # Send response status
                self.send_response(response.getcode())
                
                # Forward response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Forward response body
                response_data = response.read()
                self.wfile.write(response_data)
                
        except urllib.error.URLError as e:
            # Main app is not running
            self.send_error(502, "Main application is not available")
            logger.error(f"Failed to connect to main app: {e}")
        except Exception as e:
            # Other errors
            self.send_error(500, f"Proxy error: {str(e)}")
            logger.error(f"Proxy error: {e}")
    
    def log_message(self, format, *args):
        """Custom log format"""
        logger.info(f"Port 8080 -> 5000: {format % args}")

def check_main_app_running():
    """Check if the main application is running on port 5000"""
    try:
        with urllib.request.urlopen("http://127.0.0.1:5000/health", timeout=5) as response:
            return response.getcode() == 200
    except:
        return False

def start_port_forwarder():
    """Start the port forwarder on port 8080"""
    try:
        # Wait for main app to start
        logger.info("Waiting for main application on port 5000...")
        for i in range(30):  # Wait up to 30 seconds
            if check_main_app_running():
                logger.info("Main application detected on port 5000")
                break
            time.sleep(1)
        else:
            logger.warning("Main application not detected, starting forwarder anyway")
        
        # Start the proxy server
        with socketserver.TCPServer(("0.0.0.0", 8080), ProxyHandler) as httpd:
            logger.info("Port forwarder started on port 8080 -> forwarding to port 5000")
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            logger.info("Port 8080 already in use - another forwarder may be running")
        else:
            logger.error(f"Failed to start port forwarder: {e}")
    except KeyboardInterrupt:
        logger.info("Port forwarder shutting down")
    except Exception as e:
        logger.error(f"Port forwarder error: {e}")

if __name__ == "__main__":
    start_port_forwarder()