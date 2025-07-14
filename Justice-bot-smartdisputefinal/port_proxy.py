#!/usr/bin/env python3
"""
Simple HTTP proxy for port 8080 to 5000 forwarding
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
from urllib.error import URLError

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
        target_url = f"http://127.0.0.1:5000{self.path}"
        
        try:
            req = urllib.request.Request(target_url, method=self.command)
            
            # Copy headers
            for header, value in self.headers.items():
                if header.lower() not in ['host']:
                    req.add_header(header, value)
            
            # Handle POST data
            content_length = self.headers.get('Content-Length')
            if content_length:
                post_data = self.rfile.read(int(content_length))
                req.data = post_data
            
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.getcode())
                
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                self.wfile.write(response.read())
                
        except URLError:
            self.send_error(502, "Backend server unavailable")
        except Exception as e:
            self.send_error(500, f"Proxy error: {str(e)}")
    
    def log_message(self, format, *args):
        pass

def main():
    with socketserver.TCPServer(("0.0.0.0", 8080), ProxyHandler) as httpd:
        print("Proxy server running on port 8080 -> 5000")
        httpd.serve_forever()

if __name__ == "__main__":
    main()