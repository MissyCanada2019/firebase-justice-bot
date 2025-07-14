#!/usr/bin/env python3
"""
Minimal port 8080 server for Replit web interface compatibility
Simple HTTP server that redirects to the main application
"""

import http.server
import socketserver
from urllib.parse import urlparse
import requests

class ReplitHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            response = requests.get(f"http://localhost:5000{self.path}", timeout=10)
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                if header.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.content)
        except:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
<!DOCTYPE html>
<html><head><title>SmartDispute.ai</title></head>
<body><h1>SmartDispute.ai</h1><p>Loading application...</p></body></html>
            ''')
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            response = requests.post(f"http://localhost:5000{self.path}", data=post_data, 
                                   headers=dict(self.headers), timeout=10)
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                if header.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.content)
        except:
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", 8080), ReplitHandler) as httpd:
        httpd.serve_forever()