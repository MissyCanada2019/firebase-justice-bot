#!/usr/bin/env python3
"""
Simple HTTP redirector for SmartDispute.ai
Forwards requests from port 8080 to the main application on port 5000
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import sys
import os

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def proxy_request(self):
        target_url = f"http://localhost:5000{self.path}"
        
        try:
            # Create request with headers
            req = urllib.request.Request(target_url)
            
            # Copy headers from original request
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    req.add_header(header, value)
            
            # Handle request body for POST/PUT
            content_length = self.headers.get('Content-Length')
            if content_length:
                body = self.rfile.read(int(content_length))
                req.data = body
            
            # Make the request
            with urllib.request.urlopen(req) as response:
                # Send response status
                self.send_response(response.getcode())
                
                # Copy response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Copy response body
                self.wfile.write(response.read())
                
        except urllib.error.URLError as e:
            self.send_error(502, f"Bad Gateway: {e}")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")
    
    def log_message(self, format, *args):
        # Minimal logging
        pass

def main():
    port = 8080
    print(f"Starting proxy server on port {port}")
    print(f"Forwarding to http://localhost:5000")
    
    with socketserver.TCPServer(("", port), ProxyHandler) as httpd:
        print(f"Proxy server running at http://0.0.0.0:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down proxy server")

if __name__ == "__main__":
    main()