#!/usr/bin/env python3
"""
Simple Port Forwarder for SmartDispute.ai

This script forwards HTTP requests from port 8080 to port 5000
to ensure the application is accessible via Replit's web interface.
"""

import http.server
import socketserver
import requests
import sys

class SimpleForwarder(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Forward the request to port 5000
            print(f"Forwarding GET request from port 8080 to http://localhost:5000{self.path}")
            response = requests.get(f"http://localhost:5000{self.path}", 
                                 headers=dict(self.headers),
                                 allow_redirects=False)
            
            # Send the response back
            self.send_response(response.status_code)
            
            # Copy all headers
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()
            
            # Send response content
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"Error forwarding request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
    
    def do_POST(self):
        try:
            # Get the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Forward the request to port 5000
            print(f"Forwarding POST request from port 8080 to http://localhost:5000{self.path}")
            response = requests.post(f"http://localhost:5000{self.path}", 
                                  data=body,
                                  headers=dict(self.headers),
                                  allow_redirects=False)
            
            # Send the response back
            self.send_response(response.status_code)
            
            # Copy all headers
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()
            
            # Send response content
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"Error forwarding request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))

def run_server():
    server_address = ('', 8080)
    httpd = None
    
    # Configure the server to allow address reuse to avoid binding errors
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        # Create and start the server
        httpd = socketserver.TCPServer(server_address, SimpleForwarder)
        print(f"Port forwarder running on http://0.0.0.0:8080")
        print(f"Forwarding requests to http://localhost:5000")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the port forwarder...")
        if httpd:
            httpd.shutdown()
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
