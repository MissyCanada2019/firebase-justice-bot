#!/usr/bin/env python3

"""
Python HTTP Server for SmartDispute.ai

This script runs a simple HTTP server on port 8080 using only Python standard library.
It redirects requests to the main application running on port 5000.
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import threading
import time
import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
PORT = 8080
MAIN_APP_URL = "http://localhost:5000"

# HTML content for error pages
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - SmartDispute.ai</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .container {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .success {
            color: #27ae60;
            font-weight: bold;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
        }
        .button {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 10px 15px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
        }
        .button:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <h1>SmartDispute.ai</h1>
    
    <div class="container">
        {content}
    </div>
</body>
</html>
"""

# Function to check if the main application is running
def is_main_app_running():
    try:
        with urllib.request.urlopen(f"{MAIN_APP_URL}/health", timeout=2) as response:
            return response.getcode() == 200
    except (urllib.error.URLError, ConnectionRefusedError):
        return False

# Custom HTTP request handler
class SmartDisputeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests
        """
        try:
            # Special endpoints
            if self.path == "/health":
                self._serve_health_check()
                return
            elif self.path == "/status":
                self._serve_status_page()
                return
            
            # Check if main app is running
            if not is_main_app_running():
                self._serve_maintenance_page()
                return
            
            # Forward request to main application
            try:
                with urllib.request.urlopen(f"{MAIN_APP_URL}{self.path}", timeout=10) as response:
                    # Copy response headers
                    self.send_response(response.getcode())
                    for header, value in response.getheaders():
                        if header.lower() not in ['server', 'date', 'transfer-encoding']:
                            self.send_header(header, value)
                    self.end_headers()
                    
                    # Copy response body
                    self.wfile.write(response.read())
            except urllib.error.HTTPError as e:
                # Handle HTTP errors from the main app
                if e.code == 404:
                    self._serve_not_found()
                else:
                    self._serve_error(e.code)
            except Exception as e:
                logger.error(f"Error forwarding request: {str(e)}")
                self._serve_error(500)
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            self._serve_error(500)
    
    def do_POST(self):
        """
        Handle POST requests
        """
        try:
            # Check if main app is running
            if not is_main_app_running():
                self._serve_maintenance_page()
                return
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Forward request to main application
            req = urllib.request.Request(
                f"{MAIN_APP_URL}{self.path}",
                data=post_data,
                headers=dict(self.headers),
                method='POST'
            )
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    # Copy response headers
                    self.send_response(response.getcode())
                    for header, value in response.getheaders():
                        if header.lower() not in ['server', 'date', 'transfer-encoding']:
                            self.send_header(header, value)
                    self.end_headers()
                    
                    # Copy response body
                    self.wfile.write(response.read())
            except urllib.error.HTTPError as e:
                # Handle HTTP errors from the main app
                if e.code == 404:
                    self._serve_not_found()
                else:
                    self._serve_error(e.code)
            except Exception as e:
                logger.error(f"Error forwarding request: {str(e)}")
                self._serve_error(500)
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            self._serve_error(500)
    
    def _serve_health_check(self):
        """
        Serve a health check endpoint
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        health_data = {
            "status": "ok",
            "port": PORT,
            "main_app_running": is_main_app_running(),
            "timestamp": time.time()
        }
        
        self.wfile.write(json.dumps(health_data).encode())
    
    def _serve_status_page(self):
        """
        Serve a status page
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        main_app_running = is_main_app_running()
        status_class = "success" if main_app_running else "error"
        status_text = "Running" if main_app_running else "Not Running"
        
        content = f"""
        <h2>Server Status</h2>
        <p>Port 8080 Server: <span class="success">Running</span></p>
        <p>Main Application: <span class="{status_class}">{status_text}</span></p>
        <p>Port: {PORT}</p>
        <p>Time: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <a href="/health" class="button">View Health Data</a>
        """
        
        html = HTML_TEMPLATE.format(title="Status", content=content)
        self.wfile.write(html.encode())
    
    def _serve_maintenance_page(self):
        """
        Serve a maintenance page
        """
        self.send_response(503)
        self.send_header('Content-type', 'text/html')
        self.send_header('Retry-After', '300')
        self.end_headers()
        
        content = """
        <h2>Maintenance Mode</h2>
        <p class="error">The main application is currently unavailable.</p>
        <p>We're working to bring it back online as soon as possible.</p>
        <p>Please try again in a few minutes.</p>
        <a href="/status" class="button">Check Status</a>
        """
        
        html = HTML_TEMPLATE.format(title="Maintenance", content=content)
        self.wfile.write(html.encode())
    
    def _serve_not_found(self):
        """
        Serve a 404 Not Found page
        """
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        content = """
        <h2>404 Not Found</h2>
        <p class="error">The page you are looking for does not exist.</p>
        <p>Please check the URL and try again.</p>
        <a href="/" class="button">Return to Home</a>
        """
        
        html = HTML_TEMPLATE.format(title="Not Found", content=content)
        self.wfile.write(html.encode())
    
    def _serve_error(self, code=500):
        """
        Serve an error page
        """
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        content = f"""
        <h2>{code} Server Error</h2>
        <p class="error">Something went wrong on our end.</p>
        <p>We've been notified of the issue and are working to fix it.</p>
        <a href="/" class="button">Return to Home</a>
        <a href="/status" class="button">Check Status</a>
        """
        
        html = HTML_TEMPLATE.format(title="Server Error", content=content)
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """
        Override to use our own logger
        """
        logger.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

# Function to start the HTTP server
def run_server():
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), SmartDisputeHandler) as httpd:
            logger.info(f"Server started at http://0.0.0.0:{PORT}/")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"Port {PORT} is already in use. Please free the port and try again.")
        else:
            logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

# Main function
if __name__ == "__main__":
    logger.info(f"Starting SmartDispute.ai Python HTTP Server on port {PORT}")
    run_server()
