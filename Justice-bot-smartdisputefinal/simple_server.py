"""
Ultra-minimal HTTP server for SmartDispute.ai that uses only Python standard library
"""
import http.server
import socketserver
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get Replit domain information
replit_domains = os.environ.get('REPLIT_DOMAINS', 'not-set')
replit_dev_domain = os.environ.get('REPLIT_DEV_DOMAIN', 'not-set')

# Log environment information
logging.info(f"REPLIT_DOMAINS: {replit_domains}")
logging.info(f"REPLIT_DEV_DOMAIN: {replit_dev_domain}")

# Define port
PORT = 5000

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            # Return health status
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            health_data = {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "environment": {
                    "REPLIT_DOMAINS": replit_domains,
                    "REPLIT_DEV_DOMAIN": replit_dev_domain
                }
            }
            self.wfile.write(json.dumps(health_data).encode())
        elif self.path == '/':
            # Return simple HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>SmartDispute.ai Server Test</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #e62e2e; }}
                    .container {{ border: 1px solid #ddd; padding: 20px; border-radius: 5px; max-width: 800px; margin: 0 auto; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>SmartDispute.ai Simple Server</h1>
                    <p>If you can see this page, the simple server is working correctly!</p>
                    <p>This is a minimal HTTP server using only Python standard libraries.</p>
                    <h3>Environment Information:</h3>
                    <ul>
                        <li><strong>Time:</strong> {datetime.now().isoformat()}</li>
                        <li><strong>REPLIT_DOMAINS:</strong> {replit_domains}</li>
                        <li><strong>REPLIT_DEV_DOMAIN:</strong> {replit_dev_domain}</li>
                    </ul>
                    <h3>Available Endpoints:</h3>
                    <ul>
                        <li><a href="/health">/health</a> - JSON health check</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            # Handle 404
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1><p>The page you requested was not found.</p>")
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logging.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

def run_server():
    """Run the simple HTTP server"""
    logging.info(f"Starting simple HTTP server on port {PORT}...")
    
    # Enable address reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("0.0.0.0", PORT), SimpleHandler) as httpd:
        logging.info(f"Server running at http://0.0.0.0:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped by user.")
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            httpd.server_close()
            logging.info("Server stopped.")

if __name__ == "__main__":
    run_server()