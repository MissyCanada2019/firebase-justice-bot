#!/usr/bin/env python3
"""
Justice-Bot Port 8080 Server for Replit
"""

import http.server
import socketserver
import threading
import requests
import sys

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Forward request to main app on port 5000
            response = requests.get(f'http://localhost:5000{self.path}')
            self.send_response(response.status_code)
            
            # Copy headers
            for key, value in response.headers.items():
                if key.lower() not in ['connection', 'transfer-encoding', 'content-encoding']:
                    self.send_header(key, value)
            
            self.end_headers()
            self.wfile.write(response.content)
        except:
            self.send_response(503)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Justice-Bot is starting...</h1><p>Please refresh in a moment.</p>')
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            headers = dict(self.headers)
            headers.pop('Host', None)
            
            response = requests.post(
                f'http://localhost:5000{self.path}',
                data=post_data,
                headers=headers
            )
            
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                if key.lower() not in ['connection', 'transfer-encoding', 'content-encoding']:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)
        except:
            self.send_response(503)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logs

# Start port 8080 server
print("Starting Justice-Bot on port 8080...")
with socketserver.TCPServer(("0.0.0.0", 8080), ProxyHandler) as httpd:
    httpd.serve_forever()