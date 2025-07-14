#!/usr/bin/env python3
"""
Port 8080 forwarder for Replit web interface compatibility
Forwards all requests from port 8080 to the main application on port 5000
"""

import socketserver
import http.server
import requests
import sys

class ForwardingHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.forward_request('GET')
    
    def do_POST(self):
        self.forward_request('POST')
    
    def do_PUT(self):
        self.forward_request('PUT')
    
    def do_DELETE(self):
        self.forward_request('DELETE')
    
    def forward_request(self, method):
        try:
            # Build target URL
            target_url = f"http://localhost:5000{self.path}"
            
            # Prepare headers (exclude hop-by-hop headers)
            headers = {}
            for name, value in self.headers.items():
                if name.lower() not in ['host', 'connection', 'upgrade']:
                    headers[name] = value
            
            # Get request body for POST/PUT requests
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Make request to main application
            response = requests.request(
                method=method,
                url=target_url,
                headers=headers,
                data=body,
                stream=True,
                timeout=30
            )
            
            # Send response status
            self.send_response(response.status_code)
            
            # Forward response headers
            for name, value in response.headers.items():
                if name.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(name, value)
            
            self.end_headers()
            
            # Forward response body
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)
                    
        except requests.exceptions.ConnectionError:
            # Main app not available
            self.send_response(503)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html_response = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SmartDispute.ai - Connecting...</title>
                <meta http-equiv="refresh" content="3">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .loading { color: #0066cc; }
                </style>
            </head>
            <body>
                <h1 class="loading">SmartDispute.ai</h1>
                <p>Connecting to the main application...</p>
                <p><small>Port 8080 → Port 5000 forwarding active</small></p>
            </body>
            </html>
            """
            self.wfile.write(html_response.encode())
            
        except Exception as e:
            # Other errors
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Forwarding error: {str(e)}".encode())
    
    def log_message(self, format, *args):
        # Reduce logging noise
        pass

if __name__ == "__main__":
    PORT = 8080
    
    try:
        with socketserver.TCPServer(("", PORT), ForwardingHTTPRequestHandler) as server:
            print(f"Port {PORT} forwarder started - forwarding to port 5000")
            server.serve_forever()
    except KeyboardInterrupt:
        print(f"\nPort {PORT} forwarder stopped")
    except Exception as e:
        print(f"Error starting port {PORT} forwarder: {e}")
        sys.exit(1)