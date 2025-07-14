#!/usr/bin/env python3
"""
Simple HTTP redirector for port 8080 to ensure Replit web access
"""
import http.server
import urllib.request
import socketserver
from urllib.parse import urljoin
import threading

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def proxy_request(self):
        try:
            # Target URL on port 5000
            target_url = f"http://localhost:5000{self.path}"
            
            # Create request
            req = urllib.request.Request(target_url)
            
            # Copy headers
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    req.add_header(header, value)
            
            # Handle POST data
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req.data = post_data
            
            # Make request
            with urllib.request.urlopen(req) as response:
                # Send response
                self.send_response(response.getcode())
                
                # Copy response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Copy response body
                self.wfile.write(response.read())
                
        except Exception as e:
            self.send_error(502, f"Proxy error: {str(e)}")
    
    def log_message(self, format, *args):
        return  # Suppress logging

def start_proxy():
    with socketserver.TCPServer(("0.0.0.0", 8080), ProxyHandler) as httpd:
        print("Port 8080 proxy server started")
        httpd.serve_forever()

if __name__ == "__main__":
    start_proxy()