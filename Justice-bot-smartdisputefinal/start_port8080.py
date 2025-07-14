#!/usr/bin/env python3
"""
Persistent port 8080 server for Replit web interface
"""
import http.server
import socketserver
import urllib.request
import threading
import time
import sys

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward_request()
    
    def do_POST(self):
        self.forward_request()
    
    def do_HEAD(self):
        self.forward_request()
    
    def do_PUT(self):
        self.forward_request()
    
    def do_DELETE(self):
        self.forward_request()
    
    def forward_request(self):
        try:
            # Forward to main app on port 5000
            url = f"http://127.0.0.1:5000{self.path}"
            
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request
            req = urllib.request.Request(url, data=body, method=self.command)
            
            # Copy headers
            for name, value in self.headers.items():
                if name.lower() not in ['host', 'content-length']:
                    req.add_header(name, value)
            
            # Forward request
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.getcode())
                
                # Copy response headers
                for name, value in response.headers.items():
                    self.send_header(name, value)
                self.end_headers()
                
                # Copy response body
                self.wfile.write(response.read())
                
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(f'<h1>Proxy Error</h1><p>{e}</p>'.encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def start_server():
    try:
        # Allow socket reuse
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("0.0.0.0", 8080), ProxyHandler) as httpd:
            print("Port 8080 server started")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print("Port 8080 already in use, attempting different approach")
            # Try with different settings
            httpd = socketserver.TCPServer(("127.0.0.1", 8080), ProxyHandler)
            httpd.allow_reuse_address = True
            httpd.serve_forever()
        else:
            raise

if __name__ == "__main__":
    start_server()