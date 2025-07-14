#!/usr/bin/env python3
"""
Simple port 8080 redirector for Replit web access
Forwards all requests to the main application on port 5000
"""
import http.server
import socketserver
import urllib.request
import urllib.parse
import json
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
        try:
            # Construct URL for main app on port 5000
            target_url = f"http://127.0.0.1:5000{self.path}"
            
            # Get request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request
            req = urllib.request.Request(target_url, data=request_body)
            
            # Copy headers (excluding host)
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'content-length']:
                    req.add_header(header, value)
            
            # Make request to main app
            with urllib.request.urlopen(req, timeout=30) as response:
                # Copy response status
                self.send_response(response.getcode())
                
                # Copy response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['content-length', 'transfer-encoding']:
                        self.send_header(header, value)
                
                # Read response body
                response_body = response.read()
                self.send_header('Content-Length', str(len(response_body)))
                self.end_headers()
                
                # Send response body
                self.wfile.write(response_body)
                
        except URLError as e:
            # Main app not available
            self.send_error(502, f"Main application not available on port 5000: {e}")
        except Exception as e:
            # Other errors
            self.send_error(500, f"Proxy error: {e}")
    
    def log_message(self, format, *args):
        # Suppress logging
        pass

def main():
    port = 8080
    try:
        with socketserver.TCPServer(("0.0.0.0", port), ProxyHandler) as httpd:
            print(f"Port 8080 proxy server started, forwarding to port 5000")
            httpd.serve_forever()
    except Exception as e:
        print(f"Failed to start port 8080 server: {e}")

if __name__ == "__main__":
    main()