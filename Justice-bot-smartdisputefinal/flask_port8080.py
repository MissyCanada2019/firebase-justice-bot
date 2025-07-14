#!/usr/bin/env python3

"""
Simple Flask application that runs on port 8080 and forwards requests to port 5000
"""

import os
import sys
import requests
from flask import Flask, request, Response, redirect, url_for

app = Flask(__name__)
TARGET_PORT = 5000

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "UP", "message": "Port 8080 flask forwarder is running"}

@app.route('/')
def index():
    """Main index route"""
    try:
        # Try to forward to main app
        return redirect(f"http://localhost:{TARGET_PORT}/")
    except:
        # Fallback if forwarding fails
        return f"<h1>SmartDispute.ai</h1><p>Port 8080 forwarder is running. Main app should be available on port {TARGET_PORT}.</p>"

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    """Forward all requests to the main app"""
    target_url = f"http://localhost:{TARGET_PORT}/{path}"
    
    # Forward the request
    resp = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        stream=True
    )
    
    # Create a new Response object from the forwarded response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for name, value in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    
    response = Response(resp.content, resp.status_code, headers)
    return response

def main():
    """Run the application"""
    try:
        print(f"Starting Flask Port 8080 Forwarder to port {TARGET_PORT}...")
        print(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not set')}")
        print(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not set')}")
        app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
