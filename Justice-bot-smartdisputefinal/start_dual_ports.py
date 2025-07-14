#!/usr/bin/env python3
"""
Dual Port Starter for SmartDispute.ai
Runs the main application and ensures port 8080 access for Replit
"""
import subprocess
import time
import http.server
import socketserver
import threading
import urllib.request
import urllib.parse
from urllib.error import URLError
import logging
import signal
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Port8080Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def proxy_request(self):
        try:
            # Build target URL
            target_url = f"http://127.0.0.1:5000{self.path}"
            
            # Prepare headers (exclude host and connection)
            headers = {}
            for key, value in self.headers.items():
                if key.lower() not in ['host', 'connection']:
                    headers[key] = value
            
            # Handle request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Make request to main app
            req = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                # Send response
                self.send_response(response.status)
                
                # Forward headers
                for key, value in response.headers.items():
                    if key.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(key, value)
                self.end_headers()
                
                # Forward body
                self.wfile.write(response.read())
                
        except URLError:
            # Main app not ready, show loading page
            self.send_response(503)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Refresh', '3')
            self.end_headers()
            
            loading_page = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <title>SmartDispute.ai - Loading</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #FF0000 0%, #003366 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0;
                    }
                    .loading-container {
                        background: rgba(255, 255, 255, 0.95);
                        padding: 40px;
                        border-radius: 15px;
                        text-align: center;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    }
                    .maple-leaf { color: #FF0000; font-size: 2rem; }
                    .spinner { 
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #FF0000;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        animation: spin 2s linear infinite;
                        margin: 20px auto;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </head>
            <body>
                <div class="loading-container">
                    <i class="maple-leaf">🍁</i>
                    <h1>SmartDispute.ai</h1>
                    <div class="spinner"></div>
                    <p>Loading Canadian legal services...</p>
                    <small>This page will refresh automatically</small>
                </div>
            </body>
            </html>
            """
            self.wfile.write(loading_page.encode())
            
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Proxy Error: {str(e)}".encode())
    
    def log_message(self, format, *args):
        logger.debug(f"[8080] {format % args}")

def start_port_8080():
    """Start the port 8080 proxy server"""
    try:
        with socketserver.TCPServer(("0.0.0.0", 8080), Port8080Handler) as httpd:
            logger.info("Port 8080 proxy server started")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start port 8080 server: {e}")

def main():
    logger.info("Starting SmartDispute.ai with dual port access")
    
    # Start port 8080 proxy in background thread
    proxy_thread = threading.Thread(target=start_port_8080, daemon=True)
    proxy_thread.start()
    
    logger.info("Port 8080 proxy started in background")
    logger.info("Main application should be running on port 5000")
    logger.info("Access via port 8080 will proxy to port 5000")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down dual port server")

if __name__ == "__main__":
    main()