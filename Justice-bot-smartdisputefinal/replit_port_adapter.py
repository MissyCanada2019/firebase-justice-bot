#!/usr/bin/env python3
"""
Replit Port Adapter for SmartDispute.ai

This is a lightweight HTTP server specifically designed to adapt port 8080
to port 5000 for Replit, ensuring compatibility with Replit's web interface.

Features:
- Uses only standard library modules for maximum compatibility
- Handles both HTTP GET and POST requests
- Automatically forwards headers, cookies, and query parameters
- Provides helpful error messages when the main app is unavailable
- Low resource usage with efficient connection handling
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import urllib.parse
import time
import sys
import os
import socket
import threading

# Configuration
LISTEN_PORT = 8080
TARGET_PORT = 5000
TARGET_HOST = 'localhost'
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

class ReplitPortAdapter(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for adapting port 8080 to port 5000"""
    
    def do_GET(self):
        """Handle GET requests"""
        self.handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        self.handle_request('POST')
        
    def do_HEAD(self):
        """Handle HEAD requests"""
        self.handle_request('HEAD')
        
    def do_PUT(self):
        """Handle PUT requests"""
        self.handle_request('PUT')
        
    def do_DELETE(self):
        """Handle DELETE requests"""
        self.handle_request('DELETE')
        
    def do_OPTIONS(self):
        """Handle OPTIONS requests"""
        self.handle_request('OPTIONS')
        
    def do_PATCH(self):
        """Handle PATCH requests"""
        self.handle_request('PATCH')
    
    def handle_request(self, method):
        """Generic request handler for all HTTP methods"""
        target_url = f"http://{TARGET_HOST}:{TARGET_PORT}{self.path}"
        
        # Forward the request to the main app
        try:
            # Prepare the request
            request = urllib.request.Request(target_url, method=method)
            
            # Copy headers from the incoming request
            for header_name, header_value in self.headers.items():
                if header_name.lower() not in ('host', 'content-length'):
                    request.add_header(header_name, header_value)
            
            # Add content-length if present
            if 'Content-Length' in self.headers:
                content_length = int(self.headers['Content-Length'])
                
                # Read request body for POST/PUT/PATCH requests
                if content_length > 0 and method in ('POST', 'PUT', 'PATCH'):
                    request_body = self.rfile.read(content_length)
                    request.data = request_body
            
            # Send the request to the main app
            for attempt in range(MAX_RETRIES):
                try:
                    response = urllib.request.urlopen(request)
                    break
                except urllib.error.URLError as e:
                    if attempt < MAX_RETRIES - 1:
                        # Wait and retry
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        # Max retries reached, propagate the error
                        raise e
            
            # Send the response status code
            self.send_response(response.status)
            
            # Copy headers from the main app response
            for header in response.getheaders():
                if header[0].lower() not in ('connection', 'transfer-encoding'):
                    self.send_header(header[0], header[1])
            
            # End headers
            self.end_headers()
            
            # Send the response body
            self.wfile.write(response.read())
            
        except urllib.error.HTTPError as e:
            # Forward HTTP errors from the main app
            self.send_response(e.code)
            for header in e.headers.items():
                if header[0].lower() not in ('connection', 'transfer-encoding'):
                    self.send_header(header[0], header[1])
            self.end_headers()
            error_content = e.read()
            if error_content:
                self.wfile.write(error_content)
            
        except (urllib.error.URLError, ConnectionRefusedError) as e:
            # Main app is not available
            self.send_response(503)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            error_message = f"""<html>
<head><title>Service Unavailable</title></head>
<body>
<h1>Service Temporarily Unavailable</h1>
<p>The main application is currently starting up or unavailable.</p>
<p>Please wait a moment and refresh the page.</p>
<p>Error details: {str(e)}</p>
<script>setTimeout(function() {{ window.location.reload(); }}, 5000);</script>
</body>
</html>"""
            self.wfile.write(error_message.encode('utf-8'))
            
        except Exception as e:
            # Handle any other errors
            self.send_response(500)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            error_message = f"""<html>
<head><title>Internal Server Error</title></head>
<body>
<h1>Internal Server Error</h1>
<p>An error occurred while processing your request.</p>
<p>Error details: {str(e)}</p>
</body>
</html>"""
            self.wfile.write(error_message.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom logging that prefixes messages with port info"""
        sys.stderr.write(f"[Port {LISTEN_PORT}->Port {TARGET_PORT}] " + format % args + "\n")

def is_port_active(port):
    """Check if a port is active and responding"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_server():
    """Start the HTTP server"""
    # Create a threaded HTTP server class
    class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        pass
    server_class = ThreadingHTTPServer
    
    # Allow port reuse
    server_class.allow_reuse_address = True
    
    try:
        httpd = server_class(("", LISTEN_PORT), ReplitPortAdapter)
        print(f"Starting Replit Port Adapter on port {LISTEN_PORT}")
        print(f"Forwarding requests to port {TARGET_PORT}")
        
        # Write PID to file for management
        with open('replit_port_adapter.pid', 'w') as f:
            f.write(str(os.getpid()))
        
        # Start the server
        httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        httpd.shutdown()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {LISTEN_PORT} is already in use")
        else:
            print(f"Error starting server: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    """Main function"""
    # Wait for the main app to be available
    print(f"Waiting for main application on port {TARGET_PORT}...")
    
    for i in range(10):  # Wait up to 10 retries
        if is_port_active(TARGET_PORT):
            print(f"Main application is available on port {TARGET_PORT}")
            break
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
    else:
        print(f"\nWarning: Main application on port {TARGET_PORT} not detected")
        print("The adapter will still start and retry connections when requests arrive")
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        # Clean up PID file
        try:
            os.remove('replit_port_adapter.pid')
        except:
            pass

if __name__ == "__main__":
    main()