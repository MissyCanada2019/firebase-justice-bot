#!/usr/bin/env python3

"""
Final 8080 Server for SmartDispute.ai

This is a standalone HTTP server that runs on port 8080.
It uses only Python standard library components.
"""

import http.server
import socketserver
import json
import sys
import os
import threading
import time
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

# Custom HTTP request handler
class SmartDisputeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests
        """
        try:
            # Route paths to different handlers
            if self.path == '/' or self.path == '/index.html':
                self._serve_home_page()
            elif self.path == '/health':
                self._serve_health_check()
            elif self.path.startswith('/static/'):
                self._serve_static_file(self.path[8:])  # Remove '/static/' prefix
            else:
                self._serve_not_found()
        except Exception as e:
            logger.error(f"Error handling GET request: {str(e)}")
            self._serve_error()
    
    def do_POST(self):
        """
        Handle POST requests
        """
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Route paths to different handlers
            if self.path == '/api/login':
                self._handle_login(post_data)
            elif self.path == '/api/contact':
                self._handle_contact(post_data)
            else:
                self._serve_not_found()
        except Exception as e:
            logger.error(f"Error handling POST request: {str(e)}")
            self._serve_error()
    
    def _serve_home_page(self):
        """
        Serve the home page
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Simple HTML page
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SmartDispute.ai</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                .container {
                    background-color: #f9f9f9;
                    border-radius: 5px;
                    padding: 20px;
                    margin-top: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .success {
                    color: #27ae60;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>SmartDispute.ai</h1>
            
            <div class="container">
                <h2>Port 8080 Server</h2>
                <p>This server is running on port 8080 to support Replit deployment.</p>
                <p class="success">✓ Server is online and ready</p>
            </div>
            
            <div class="container">
                <h2>Server Information</h2>
                <ul>
                    <li><strong>Server Type:</strong> Pure Python HTTP</li>
                    <li><strong>Port:</strong> 8080</li>
                    <li><strong>Status:</strong> Active</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
    
    def _serve_health_check(self):
        """
        Serve a health check endpoint
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        health_data = {
            "status": "ok",
            "service": "SmartDispute.ai",
            "port": PORT,
            "server_type": "pure_python",
            "timestamp": time.time()
        }
        
        self.wfile.write(json.dumps(health_data).encode())
    
    def _serve_static_file(self, file_path):
        """
        Serve a static file
        """
        # Security check to prevent directory traversal
        if '..' in file_path or file_path.startswith('/'):
            self._serve_not_found()
            return
        
        # Check if file exists in the static directory
        full_path = os.path.join('static', file_path)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            self._serve_not_found()
            return
        
        # Determine content type based on file extension
        content_type = 'text/plain'
        if file_path.endswith('.html'):
            content_type = 'text/html'
        elif file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif file_path.endswith('.png'):
            content_type = 'image/png'
        elif file_path.endswith('.gif'):
            content_type = 'image/gif'
        
        # Serve the file
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Content-length', len(content))
                self.end_headers()
                
                self.wfile.write(content)
        except Exception as e:
            logger.error(f"Error serving static file {file_path}: {str(e)}")
            self._serve_error()
    
    def _handle_login(self, post_data):
        """
        Handle login request
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": "This is a mock response. In the real application, this would authenticate a user."
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_contact(self, post_data):
        """
        Handle contact form submission
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "success",
            "message": "Message received. In the real application, this would send a contact form."
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _serve_not_found(self):
        """
        Serve a 404 Not Found response
        """
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        not_found_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Not Found - SmartDispute.ai</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                    text-align: center;
                }
                h1 {
                    color: #e74c3c;
                    font-size: 36px;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f9f9f9;
                    border-radius: 5px;
                    padding: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                a {
                    color: #3498db;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404 Not Found</h1>
                <p>The page you are looking for does not exist.</p>
                <p><a href="/">Return to Home Page</a></p>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(not_found_html.encode())
    
    def _serve_error(self):
        """
        Serve a 500 Internal Server Error response
        """
        self.send_response(500)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        error_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Server Error - SmartDispute.ai</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    color: #333;
                    text-align: center;
                }
                h1 {
                    color: #e74c3c;
                    font-size: 36px;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f9f9f9;
                    border-radius: 5px;
                    padding: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                a {
                    color: #3498db;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>500 Internal Server Error</h1>
                <p>Something went wrong on our end. Please try again later.</p>
                <p><a href="/">Return to Home Page</a></p>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Override to use our own logger"""
        logger.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

# Main function to run the server
def main():
    # Create PID file
    with open('final_8080.pid', 'w') as f:
        f.write(str(os.getpid()))
    
    # Log server startup
    logger.info(f"Starting SmartDispute.ai server on port {PORT}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Create a 'static' directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Start the HTTP server
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), SmartDisputeHandler) as httpd:
            logger.info(f"Server started at port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        # Clean up PID file on exit
        if os.path.exists('final_8080.pid'):
            os.remove('final_8080.pid')
        logger.info("Server stopped")

# Run the server if script is executed directly
if __name__ == "__main__":
    main()
