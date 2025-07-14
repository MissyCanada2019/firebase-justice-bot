# Simple Flask application for port 8080 forwarding
# Specifically designed for Replit environment

import os
import logging
import requests
from flask import Flask, request, Response, redirect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('replit_port_8080')

# Configuration
TARGET_PORT = 5000
LISTEN_PORT = 8080
TARGET_HOST = 'localhost'

# Create Flask app
app = Flask(__name__)

# Get Replit domain information
REPLIT_DOMAINS = os.environ.get('REPLIT_DOMAINS', '')
REPLIT_DEV_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', '')

logger.info(f"REPLIT_DOMAINS: {REPLIT_DOMAINS}")
logger.info(f"REPLIT_DEV_DOMAIN: {REPLIT_DEV_DOMAIN}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    """Forward all requests to the main application"""
    target_url = f'http://{TARGET_HOST}:{TARGET_PORT}/{path}'
    logger.info(f"Forwarding {request.method} request to {target_url}")
    
    # Handle different HTTP methods
    method = getattr(requests, request.method.lower())
    
    try:
        # Forward the request
        resp = method(
            target_url,
            data=request.get_data(),
            headers={key: value for key, value in request.headers.items() if key != 'Host'},
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )
        
        # Create response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        # Return the response
        return Response(resp.content, resp.status_code, headers)
        
    except requests.exceptions.ConnectionError:
        # Main app not available
        return """
        <html>
            <head><title>Service Unavailable</title></head>
            <body>
                <h1>Service Temporarily Unavailable</h1>
                <p>The main application is currently starting up.</p>
                <p>Please wait a moment and refresh the page.</p>
                <script>setTimeout(function() { window.location.reload(); }, 5000);</script>
            </body>
        </html>
        """, 503

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "port": LISTEN_PORT, "target_port": TARGET_PORT}

@app.route('/info')
def info():
    """Information endpoint"""
    return {
        "status": "ok",
        "port": LISTEN_PORT,
        "target_port": TARGET_PORT,
        "replit_domains": REPLIT_DOMAINS,
        "replit_dev_domain": REPLIT_DEV_DOMAIN
    }

if __name__ == "__main__":
    # Startup message
    print(f"Starting Replit port 8080 adapter")
    print(f"Forwarding requests from port {LISTEN_PORT} to port {TARGET_PORT}")
    
    # Run the app
    app.run(host='0.0.0.0', port=LISTEN_PORT, debug=False, threaded=True)