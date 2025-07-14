#!/usr/bin/env python3
"""
Simple HTTP Server for port 8080
This script creates a very simple HTTP server that listens on port 8080 
and redirects all requests to the primary application domain.
"""
import http.server
import socketserver
import threading
import os
import sys
import time

# Get the Replit domain from environment
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN")

class SimpleRedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests with redirect to Replit domain"""
        if self.path == "/health" or self.path == "/health/":
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            return
            
        # Redirect to the Replit domain (which serves the app on port 5000)
        if REPLIT_DOMAIN:
            self.send_response(302)  # Found/Redirect
            redirect_url = f"https://{REPLIT_DOMAIN}{self.path}"
            self.send_header('Location', redirect_url)
            self.end_headers()
            print(f"Redirected GET {self.path} to {redirect_url}")
        else:
            # If REPLIT_DOMAIN is not available, show an error
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <head><title>Error</title></head>
            <body>
                <h1>Error: Replit domain not found</h1>
                <p>The application domain could not be determined from environment variables.</p>
            </body>
            </html>
            """)
    
    def do_POST(self):
        """Handle POST requests - redirect to Replit domain"""
        if REPLIT_DOMAIN:
            self.send_response(307)  # Temporary redirect preserving POST
            redirect_url = f"https://{REPLIT_DOMAIN}{self.path}"
            self.send_header('Location', redirect_url)
            self.end_headers()
            print(f"Redirected POST {self.path} to {redirect_url}")
        else:
            # No Replit domain
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Error: Replit domain not found")
            
    def log_message(self, format, *args):
        """Disable detailed logging to reduce noise"""
        pass

def run_server():
    """Run the HTTP server"""
    PORT = 8080
    print(f"Starting simple HTTP redirect server on port {PORT}")
    print(f"Redirecting requests to Replit domain: {REPLIT_DOMAIN}")
    
    # Enable port reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), SimpleRedirectHandler) as httpd:
            print(f"Server running at http://0.0.0.0:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not REPLIT_DOMAIN:
        print("Warning: REPLIT_DEV_DOMAIN environment variable not found!")
        print("Redirects will not work without this domain information.")
    
    # Start server in a thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped")