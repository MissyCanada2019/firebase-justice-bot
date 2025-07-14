"""
Port Adapting Server for SmartDispute.ai

This server runs on port 8080 and proxies requests to the main application on port 5000.
This allows the application to be accessed via Replit's web interface, which seems to favor port 8080.
"""
import os
import sys
import logging
import requests
import threading
import time
from flask import Flask, Response, request as flask_request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get Replit environment variables
REPLIT_DOMAINS = os.environ.get('REPLIT_DOMAINS', 'not-set')
REPLIT_DEV_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'not-set')

# Log environment variables
logger.info(f"Starting Port Adapting Server on port 8080 with environment:")
logger.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
logger.info(f"REPLIT_DOMAINS: {REPLIT_DOMAINS}")
logger.info(f"REPLIT_DEV_DOMAIN: {REPLIT_DEV_DOMAIN}")

# Create a Flask app for the port adapter
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-key-change-me')

# Target application URL
TARGET_URL = 'http://localhost:5000'

# Flag to indicate when the main app is ready
main_app_ready = False

def check_main_app():
    """Check if the main application is ready"""
    global main_app_ready
    while True:
        try:
            response = requests.get(f"{TARGET_URL}/health", timeout=1)
            if response.status_code == 200:
                logger.info("Main application is ready")
                main_app_ready = True
                return
        except Exception as e:
            logger.debug(f"Main application check failed: {e}")
            main_app_ready = False
        time.sleep(2)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Proxy all requests to the main application"""
    global main_app_ready
    
    if not main_app_ready:
        return fallback()
        
    # Build the URL to forward to
    target_url = f"{TARGET_URL}/{path}"
    
    # Get the same HTTP method that was used to request this endpoint
    method = flask_request.method
    
    # Get query string parameters
    params = flask_request.args
    
    # Get request headers
    headers = {key: value for key, value in flask_request.headers if key.lower() != 'host'}
    
    # Get request body for POST, PUT, PATCH requests
    data = flask_request.get_data() if method in ['POST', 'PUT', 'PATCH'] else None
    
    try:
        # Make request to target server
        response = requests.request(
            method=method,
            url=target_url,
            params=params,
            headers=headers,
            data=data,
            cookies=flask_request.cookies,
            allow_redirects=False,
            timeout=10
        )
        
        # Create Flask Response object
        proxy_response = Response(
            response.content,
            status=response.status_code
        )
        
        # Add headers from proxied response
        for key, value in response.headers.items():
            if key.lower() not in ['transfer-encoding', 'content-encoding', 'content-length']:
                proxy_response.headers[key] = value
                
        return proxy_response
        
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return fallback()

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'ok',
        'port': 8080,
        'main_app_ready': main_app_ready,
        'proxy_target': TARGET_URL,
        'env': {
            'REPLIT_DOMAINS': REPLIT_DOMAINS,
            'REPLIT_DEV_DOMAIN': REPLIT_DEV_DOMAIN
        }
    }

def fallback():
    """Fallback page when main app isn't available yet"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartDispute.ai - Loading</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body {{
                background-color: #212529;
                color: #f8f9fa;
                font-family: 'Inter', sans-serif;
                padding-top: 40px;
                text-align: center;
            }}
            .logo {{
                max-width: 300px;
                margin-bottom: 20px;
            }}
            .loading-container {{
                width: 80%;
                max-width: 600px;
                margin: 0 auto;
                padding: 30px;
                background-color: #343a40;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.3);
            }}
            .spinner-border {{
                width: 3rem;
                height: 3rem;
                margin: 20px auto;
            }}
            .refresh-btn {{
                margin-top: 20px;
            }}
        </style>
        <script>
            // Auto-refresh the page after 5 seconds
            setTimeout(function() {{
                window.location.reload();
            }}, 5000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="loading-container">
                <h1>SmartDispute.ai</h1>
                <h2>Your Legal Advocate</h2>
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="lead">Starting the application...</p>
                <p>The SmartDispute.ai platform is initializing and will be available shortly.</p>
                <p>Environment: {REPLIT_DEV_DOMAIN}</p>
                <button class="btn btn-primary refresh-btn" onclick="window.location.reload()">
                    Refresh Now
                </button>
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    # Start health check thread
    check_thread = threading.Thread(target=check_main_app)
    check_thread.daemon = True
    check_thread.start()
    
    # Start the Flask app on port 8080
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False, threaded=True)