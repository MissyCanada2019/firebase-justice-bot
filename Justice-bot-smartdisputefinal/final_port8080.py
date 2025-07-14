#!/usr/bin/env python3
"""
Final port 8080 solution for Replit web interface
Simple HTTP proxy that forwards requests to the main application
"""

import http.server
import socketserver
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def proxy_request(self):
        try:
            # Build target URL
            target_url = f"http://localhost:5000{self.path}"
            
            # Handle POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = None
            if content_length > 0:
                post_data = self.rfile.read(content_length)
            
            # Create request
            req = urllib.request.Request(target_url, data=post_data)
            
            # Copy important headers
            for name, value in self.headers.items():
                if name.lower() not in ['host', 'connection', 'content-length']:
                    req.add_header(name, value)
            
            # Set proper host header
            req.add_header('Host', 'localhost:5000')
            
            # Make request
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.getcode())
                
                # Copy response headers
                for name, value in response.headers.items():
                    if name.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(name, value)
                
                self.end_headers()
                self.wfile.write(response.read())
                
        except urllib.error.URLError:
            # Fallback response
            self.send_response(503)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Refresh', '5')
            self.end_headers()
            
            html = """<!DOCTYPE html>
<html>
<head>
    <title>SmartDispute.ai - Loading</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .loading { color: #0066cc; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>
</head>
<body>
    <h1 class="loading">SmartDispute.ai</h1>
    <p>Connecting to main application...</p>
    <p><small>Please wait while we establish the connection.</small></p>
</body>
</html>"""
            self.wfile.write(html.encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
    
    def log_message(self, format, *args):
        # Reduce logging noise
        pass

if __name__ == "__main__":
    PORT = 8080
    with socketserver.TCPServer(("0.0.0.0", PORT), ProxyHandler) as httpd:
        print(f"Port {PORT} proxy running - forwarding to port 5000")
        httpd.serve_forever()