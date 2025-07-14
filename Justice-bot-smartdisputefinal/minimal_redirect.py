#!/usr/bin/env python3
"""
Minimal HTTP redirection server for port 8080
This script creates a very simple HTTP server that listens on port 8080
and redirects all requests to the Replit domain (which serves the app on port 5000)
"""
import http.server
import socketserver
import logging
import os
import time
import threading
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PORT = 8080
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN", "")

class MinimalRedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests with a redirect to the Replit domain"""
        try:
            if REPLIT_DOMAIN:
                # If we have a Replit domain, redirect to it
                self.send_response(302)
                redirect_url = f"https://{REPLIT_DOMAIN}{self.path}"
                self.send_header('Location', redirect_url)
                self.end_headers()
                logger.info(f"Redirected GET {self.path} to {redirect_url}")
            else:
                # No Replit domain, show a simple page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <head><title>SmartDispute.ai</title></head>
                <body>
                    <h1>SmartDispute.ai</h1>
                    <p>The application is running on port 5000.</p>
                    <p>Please access through the Replit domain.</p>
                </body>
                </html>
                """)
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Internal server error")

    def do_POST(self):
        """Handle POST requests with a redirect to the Replit domain"""
        try:
            if REPLIT_DOMAIN:
                # If we have a Replit domain, redirect to it
                self.send_response(307)  # Temporary redirect preserving POST
                redirect_url = f"https://{REPLIT_DOMAIN}{self.path}"
                self.send_header('Location', redirect_url)
                self.end_headers()
                logger.info(f"Redirected POST {self.path} to {redirect_url}")
            else:
                # No Replit domain, return error
                self.send_response(503)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Service unavailable - Replit domain not found")
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Internal server error")
    
    def log_message(self, format, *args):
        """Limit logging to reduce noise"""
        pass

def run_server():
    """Run the HTTP server on port 8080"""
    logger.info(f"Starting minimal redirection server on port {PORT}")
    
    # Create server with address reuse enabled
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), MinimalRedirectHandler) as httpd:
            logger.info(f"Server running at 0.0.0.0:{PORT}, redirecting to {REPLIT_DOMAIN}")
            
            # Store server reference for clean shutdown
            global server_instance
            server_instance = httpd
            
            # Run server
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error running HTTP server: {e}")

def signal_handler(sig, frame):
    """Signal handler for graceful shutdown"""
    logger.info("Shutdown requested, stopping server...")
    if 'server_instance' in globals():
        server_instance.shutdown()
    sys.exit(0)

if __name__ == "__main__":
    # Print Replit info
    logger.info(f"REPLIT_DEV_DOMAIN: {REPLIT_DOMAIN}")
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get environment info
    pid = os.getpid()
    logger.info(f"Starting minimal redirection server with PID {pid}")
    
    # Save PID to file for external management
    with open("minimal_redirect.pid", "w") as f:
        f.write(str(pid))
    
    # Create and start server thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server stopping due to keyboard interrupt")
    finally:
        # Cleanup PID file
        if os.path.exists("minimal_redirect.pid"):
            os.remove("minimal_redirect.pid")
        logger.info("Server stopped")