"""
Ultra-minimal server for SmartDispute.ai that responds immediately to Replit port checks
without any dependencies
"""
import os
import http.server
import socketserver
import threading
import logging
import time
# This server doesn't use Flask

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log domain information
REPLIT_DOMAINS = os.environ.get('REPLIT_DOMAINS', 'not-set')
REPLIT_DEV_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'not-set')

logger.info(f"Starting minimal server with environment:")
logger.info(f"REPLIT_DOMAINS: {REPLIT_DOMAINS}")
logger.info(f"REPLIT_DEV_DOMAIN: {REPLIT_DEV_DOMAIN}")

# HTML Content
HTML = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SmartDispute.ai - Ultra Minimal Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #222; color: #eee; }}
        h1 {{ color: #e62e2e; }}
        .container {{ border: 1px solid #444; padding: 20px; border-radius: 5px; max-width: 800px; margin: 0 auto; }}
        .success {{ color: #4CAF50; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SmartDispute.ai Ultra-Minimal Server</h1>
        <h2 class="success">Success! Server is running!</h2>
        
        <p>
            If you can see this page, that means our server is 
            accessible through the Replit proxy system.
        </p>
        
        <h3>Environment Information:</h3>
        <ul>
            <li>REPLIT_DOMAINS: {REPLIT_DOMAINS}</li>
            <li>REPLIT_DEV_DOMAIN: {REPLIT_DEV_DOMAIN}</li>
            <li>Server Time: <span id="server-time"></span></li>
        </ul>
        
        <p>Try both of these links:</p>
        <ul>
            <li><a href="/" style="color: #3498db;">Root URL</a></li>
            <li><a href="/health" style="color: #3498db;">Health Check</a></li>
        </ul>
    </div>
    
    <script>
        // Update server time
        document.getElementById('server-time').innerText = new Date().toLocaleString();
    </script>
</body>
</html>
"""

class MinimalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve a simple loading page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if self.path == '/health':
            self.wfile.write(b'{"status": "ok", "server": "ultra-minimal"}')
        else:
            self.wfile.write(HTML.encode())
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

def run_server_port_8080():
    # Run server on port 8080
    port = 8080
    logger.info(f"Starting ultra-minimal HTTP server on port {port}")
    
    with socketserver.TCPServer(("0.0.0.0", port), MinimalHandler) as httpd:
        logger.info(f"Server running at http://0.0.0.0:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

def run_server_port_5000():
    # Run server on port 5000
    port = 5000
    logger.info(f"Starting ultra-minimal HTTP server on port {port}")
    
    with socketserver.TCPServer(("0.0.0.0", port), MinimalHandler) as httpd:
        logger.info(f"Server running at http://0.0.0.0:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

if __name__ == "__main__":
    # Start port 8080 server in a thread
    thread_8080 = threading.Thread(target=run_server_port_8080)
    thread_8080.daemon = True
    thread_8080.start()
    
    # Run port 5000 server on the main thread
    run_server_port_5000()