#!/usr/bin/env python3
"""
Minimal HTTP server for port 8080
This just redirects all requests to port 5000
"""
import http.server
import socketserver
import logging
import threading
import os
import time
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PORT = 8080
MAIN_APP_PORT = 5000
MAIN_APP_URL = f"http://localhost:{MAIN_APP_PORT}"

class SimpleRedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests by forwarding to the main app"""
        try:
            # Log request
            logger.info(f"Received GET request for {self.path}")
            
            # Try to get content from the main app
            try:
                response = requests.get(f"{MAIN_APP_URL}{self.path}", timeout=5)
                self.send_response(response.status_code)
                
                # Copy headers
                for header, value in response.headers.items():
                    if header.lower() != 'transfer-encoding':
                        self.send_header(header, value)
                self.end_headers()
                
                # Send content
                self.wfile.write(response.content)
            except requests.RequestException as e:
                # Handle error by sending a simple HTML response
                logger.error(f"Error forwarding to main app: {e}")
                self.send_response(503)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"""
                <html>
                <head><title>SmartDispute.ai - Service Starting</title></head>
                <body>
                    <h1>SmartDispute.ai is starting up...</h1>
                    <p>The main application is starting. Please wait a moment and try refreshing.</p>
                    <p>Error: {str(e)}</p>
                </body>
                </html>
                """.encode('utf-8'))
        except Exception as e:
            logger.error(f"Unhandled error in do_GET: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Internal server error")

    def do_POST(self):
        """Handle POST requests by redirecting to the main application domain"""
        self.send_response(307)  # Temporary redirect
        replit_domain = os.environ.get("REPLIT_DEV_DOMAIN")
        if replit_domain:
            redirect_url = f"https://{replit_domain}{self.path}"
        else:
            redirect_url = f"http://localhost:{MAIN_APP_PORT}{self.path}"
        self.send_header('Location', redirect_url)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(format % args)

def run_server():
    """Run the HTTP server"""
    logger.info(f"Starting minimal HTTP server on port {PORT}")
    
    # Create server with reuse_port option
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), SimpleRedirectHandler) as httpd:
            logger.info(f"Server running at 0.0.0.0:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error running HTTP server: {e}")

if __name__ == "__main__":
    # Print environment info
    logger.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
    logger.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not found')}")
    logger.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not found')}")
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Keep the main thread alive to prevent the program from exiting
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server stopped")