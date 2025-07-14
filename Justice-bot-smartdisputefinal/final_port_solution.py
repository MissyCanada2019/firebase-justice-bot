#!/usr/bin/env python3
"""
Final Port 8080 Solution for SmartDispute.ai
This script creates a minimal HTTP server on port 8080 that always returns a redirect
to the Replit domain directly.

After 3 days of trying complex port forwarding solutions, this simplified approach
has the highest chance of working in the Replit environment.
"""
import http.server
import socketserver
import os
import sys

# Get the Replit domain from environment variables
REPLIT_DOMAIN = os.environ.get("REPLIT_DEV_DOMAIN") or os.environ.get("REPLIT_DOMAINS")
if REPLIT_DOMAIN and "," in REPLIT_DOMAIN:
    REPLIT_DOMAIN = REPLIT_DOMAIN.split(",")[0].strip()

if not REPLIT_DOMAIN:
    print("ERROR: REPLIT_DOMAIN not found in environment variables", file=sys.stderr)
    REPLIT_DOMAIN = "your-replit-domain.replit.dev"  # Placeholder in case it's not found

class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Always redirect to the same Replit domain directly"""
        target_url = f"https://{REPLIT_DOMAIN}{self.path}"
        
        self.send_response(302)  # Found/Redirect
        self.send_header('Location', target_url)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Send a simple message with redirect
        message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirecting...</title>
            <meta http-equiv="refresh" content="0;url={target_url}">
        </head>
        <body>
            <h1>Redirecting to SmartDispute.ai</h1>
            <p>If you are not redirected automatically, click <a href="{target_url}">here</a>.</p>
            <p>Original path: {self.path}</p>
            <p>Target: {target_url}</p>
        </body>
        </html>
        """
        self.wfile.write(message.encode('utf-8'))
        print(f"Redirected {self.path} to {target_url}")
        
    def do_POST(self):
        """Handle POST requests the same way - with redirect"""
        self.do_GET()
        
    def log_message(self, format, *args):
        """Minimal logging to stdout"""
        sys.stdout.write(f"{self.client_address[0]} - {format % args}\n")
        sys.stdout.flush()

def main():
    port = 8080
    print(f"Starting minimal redirect server on port {port}")
    print(f"All requests will be redirected to: https://{REPLIT_DOMAIN}/")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), RedirectHandler) as httpd:
            print(f"Server running at http://0.0.0.0:{port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())