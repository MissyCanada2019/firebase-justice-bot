#!/usr/bin/env python3
"""
Start both the main application and port 8080 forwarder
"""
import subprocess
import threading
import time
import signal
import sys
import http.server
import urllib.request

class SimpleForwarder(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward_request()
    
    def do_POST(self):
        self.forward_request()
    
    def forward_request(self):
        try:
            # Forward to main app on port 5000
            target_url = f"http://localhost:5000{self.path}"
            
            # Handle POST data
            content_length = int(self.headers.get('content-length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            req = urllib.request.Request(target_url, data=post_data)
            
            # Copy important headers
            for header in ['content-type', 'authorization', 'cookie']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])
            
            with urllib.request.urlopen(req, timeout=10) as response:
                self.send_response(response.getcode())
                
                # Copy response headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                
                self.end_headers()
                self.wfile.write(response.read())
                
        except Exception as e:
            # Service unavailable page
            self.send_response(503)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
            <html>
                <head>
                    <title>SmartDispute.ai - Starting</title>
                    <meta http-equiv="refresh" content="3">
                </head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1>SmartDispute.ai</h1>
                    <p>The application is starting up...</p>
                    <p>This page will automatically refresh.</p>
                    <small>Error: {str(e)}</small>
                </body>
            </html>
            """.encode())
    
    def log_message(self, format, *args):
        pass  # Reduce log noise

def run_forwarder():
    """Run the port 8080 forwarder"""
    server = http.server.HTTPServer(('0.0.0.0', 8080), SimpleForwarder)
    print("Port 8080 forwarder started")
    server.serve_forever()

def main():
    """Start the forwarder and keep it running"""
    print("Starting SmartDispute.ai port 8080 forwarder...")
    
    # Start forwarder in daemon thread
    forwarder_thread = threading.Thread(target=run_forwarder)
    forwarder_thread.daemon = True
    forwarder_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()