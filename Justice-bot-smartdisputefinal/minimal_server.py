#!/usr/bin/env python3
"""
Ultra-minimal server for SmartDispute.ai that responds immediately to Replit port checks
without any dependencies
"""

import http.server
import socketserver

class MinimalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve a simple loading page"""
        # Send a successful response with HTML content
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # HTML content for the loading page
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>SmartDispute.ai</title>
            <meta http-equiv="refresh" content="0;URL='http://localhost:5000'"> 
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #1e1e1e;
                    color: #ffffff;
                    text-align: center;
                    padding-top: 100px;
                    margin: 0;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #2d2d2d;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                }
                h1 {
                    color: #4dabf7;
                }
                .loader {
                    border: 8px solid #3d3d3d;
                    border-radius: 50%;
                    border-top: 8px solid #4dabf7;
                    width: 60px;
                    height: 60px;
                    margin: 20px auto;
                    animation: spin 1.5s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                p {
                    font-size: 18px;
                    line-height: 1.6;
                }
                .status {
                    margin-top: 20px;
                    font-style: italic;
                    color: #adb5bd;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>SmartDispute.ai</h1>
                <div class="loader"></div>
                <p>Redirecting to main application...</p>
                <p class="status">If you're not redirected automatically, <a href="http://localhost:5000" style="color: #4dabf7;">click here</a>.</p>
            </div>
        </body>
        </html>
        '''
        
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        # Uncomment the line below if you want to see log messages
        # print(format % args)
        pass

def run_server():
    """Run the minimal server on port 8080"""
    try:
        with socketserver.TCPServer(('0.0.0.0', 8080), MinimalHandler) as httpd:
            print("Minimal server running on port 8080")
            httpd.serve_forever()
    except Exception as e:
        print(f"Error starting minimal server: {e}")

if __name__ == "__main__":
    run_server()