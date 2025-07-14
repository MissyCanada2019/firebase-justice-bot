#!/usr/bin/env python3

"""
Simplified HTTP Server for port 8080

This script creates a basic HTTP server on port 8080 with minimal dependencies.
It serves a static HTML page with information about SmartDispute.ai.
"""

import http.server
import socketserver
import os
import datetime

# Constants
PORT = 8080

# HTML template
HTML_TEMPLATE = """
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
            background-color: #f5f5f5;
        }
        h1, h2 {
            color: #2c3e50;
        }
        h1 {
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
        .footer {
            margin-top: 30px;
            font-size: 0.9em;
            text-align: center;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <h1>SmartDispute.ai</h1>
    
    <div class="container">
        <h2>Welcome to SmartDispute.ai</h2>
        <p>SmartDispute.ai is an AI-powered legal automation platform designed to make legal self-advocacy accessible to everyday Canadians.</p>
        <p>Our system helps users navigate housing disputes, credit issues, and systemic injustice without legal representation.</p>
    </div>
    
    <div class="container">
        <h2>Key Features</h2>
        <ul>
            <li><strong>Document Analysis:</strong> Upload documents and get AI-assisted analysis</li>
            <li><strong>Case Merit Assessment:</strong> Evaluate your case with legal precedent</li>
            <li><strong>Automated Form Generation:</strong> Create legally-compliant documents</li>
            <li><strong>Jurisdiction Support:</strong> Customized for Canadian legal requirements</li>
        </ul>
    </div>
    
    <div class="container">
        <h2>Contact Information</h2>
        <p>For more information or assistance, please contact us:</p>
        <p>Email: smartdisputecanada@gmail.com</p>
        <p>Phone: 1-226-907-0942</p>
    </div>
    
    <div class="container">
        <h2>Server Information</h2>
        <p>Server running on port: {port}</p>
        <p>Current time: {time}</p>
        <p>Hosted on Replit: {is_replit}</p>
    </div>
    
    <div class="footer">
        <p>&copy; {year} SmartDispute.ai. All rights reserved.</p>
    </div>
</body>
</html>
"""

# Request handler
class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self._serve_health_check()
        else:
            self._serve_html_page()
    
    def _serve_health_check(self):
        """Serve a health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        health_data = '{"status":"ok","port":' + str(PORT) + '}'
        self.wfile.write(health_data.encode())
    
    def _serve_html_page(self):
        """Serve a static HTML page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Format the template with dynamic values
        now = datetime.datetime.now()
        html = HTML_TEMPLATE.format(
            port=PORT,
            time=now.strftime("%Y-%m-%d %H:%M:%S"),
            is_replit="Yes" if os.environ.get("REPLIT_DEPLOYMENT") else "No",
            year=now.year
        )
        
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Custom logging to stdout"""
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

# Main function
def main():
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), SimpleHandler) as httpd:
            print(f"Server started at http://0.0.0.0:{PORT}/")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Error: {str(e)}")

# Start the server
if __name__ == "__main__":
    print(f"Starting simplified HTTP server on port {PORT}")
    main()
