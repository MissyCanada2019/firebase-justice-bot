"""
Quick server optimized for Replit's proxy configuration
"""
from flask import Flask, request, jsonify
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
logging.info(f"Starting quick server with domains: {replit_domains}")

@app.route('/')
def home():
    """Home page - return simple HTML"""
    user_agent = request.headers.get('User-Agent', 'Unknown')
    client_ip = request.remote_addr
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartDispute.ai Quick Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #e62e2e; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .info {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
            pre {{ background-color: #eee; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SmartDispute.ai Quick Server</h1>
            <p>If you're seeing this, the Quick Server is running correctly on Replit!</p>
            
            <div class="info">
                <h2>Request Information</h2>
                <p><strong>User-Agent:</strong> {user_agent}</p>
                <p><strong>Client IP:</strong> {client_ip}</p>
                <p><strong>Request Headers:</strong></p>
                <pre>{dict(request.headers)}</pre>
            </div>
            
            <div class="info">
                <h2>Environment</h2>
                <p><strong>REPLIT_DOMAINS:</strong> {replit_domains}</p>
                <p><strong>REPLIT_DEV_DOMAIN:</strong> {replit_dev_domain}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "env": {
            "REPLIT_DOMAINS": replit_domains,
            "REPLIT_DEV_DOMAIN": replit_dev_domain,
        },
        "headers": dict(request.headers),
        "remote_addr": request.remote_addr
    })

if __name__ == "__main__":
    # Important: Use 0.0.0.0 to listen on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)