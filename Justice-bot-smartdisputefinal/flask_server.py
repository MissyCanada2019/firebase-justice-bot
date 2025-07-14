"""
Ultra minimal Flask server specifically designed for Replit
"""
from flask import Flask, request, jsonify, redirect
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Get environment variables
replit_domains = os.environ.get('REPLIT_DOMAINS', 'not-set')
replit_dev_domain = os.environ.get('REPLIT_DEV_DOMAIN', 'not-set')

# Log the current environment
logging.info(f"Starting Flask server with domains: {replit_domains}")

@app.route('/')
def home():
    """Home page - return simple HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartDispute.ai Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #e62e2e; }
            .container { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SmartDispute.ai Test Server</h1>
            <p>If you're seeing this page, the web server is working!</p>
            <p>Click <a href="/main">here</a> to go to the main SmartDispute application.</p>
        </div>
    </body>
    </html>
    """

@app.route('/main')
def main_app():
    """Redirect to the main application"""
    return redirect('/static/index.html')

@app.route('/hello')
def hello():
    return "Hello from SmartDispute.ai test server!"

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "env": {
            "REPLIT_DOMAINS": replit_domains,
            "REPLIT_DEV_DOMAIN": replit_dev_domain,
        }
    })

@app.route('/debug')
def debug():
    """Debug endpoint to see request information"""
    return jsonify({
        "headers": dict(request.headers),
        "env": dict(os.environ),
        "remote_addr": request.remote_addr,
        "url": request.url,
        "path": request.path,
        "method": request.method
    })

if __name__ == "__main__":
    # Important: Use 0.0.0.0 to listen on all interfaces
    app.run(host='0.0.0.0', port=5000)