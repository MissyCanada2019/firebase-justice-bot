#!/usr/bin/env python3
"""
Pure Python HTTP server for port 8080
Doesn't rely on Flask or any external dependencies
"""

import http.server
import socketserver
import json
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
PORT = 8080

# Custom request handler
class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""<html>
                <head><title>SmartDispute.ai</title></head>
                <body>
                <h1>SmartDispute.ai</h1>
                <p>Pure Python port 8080 server</p>
                </body>
                </html>""")
                
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                health_data = {
                    "status": "ok",
                    "port": PORT,
                    "server": "pure_python"
                }
                self.wfile.write(json.dumps(health_data).encode())
                
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<h1>404 Not Found</h1><p>The requested path was not found.</p>")
                
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>500 Internal Server Error</h1>")
    
    def log_message(self, format, *args):
        """Override to use our custom logger"""
        logger.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

# Main function
def main():
    logger.info(f"Starting pure Python HTTP server on port {PORT}")
    
    # Create a PID file
    with open('pure_8080.pid', 'w') as f:
        f.write(str(os.getpid()))
    
    # Start the server
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), SimpleHandler) as httpd:
            logger.info(f"Server started at port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        # Clean up PID file
        if os.path.exists('pure_8080.pid'):
            os.remove('pure_8080.pid')

# Run the main function
if __name__ == "__main__":
    main()
