#!/usr/bin/env python3
"""
Absolutely minimal Flask server for port 8080
"""

import os
import logging
import socket
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Create a basic Flask application
app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>SmartDispute.ai</h1><p>Minimal port 8080 server</p>"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "port": 8080})

if __name__ == '__main__':
    # Always use port 8080
    port = 8080
    logger.info(f"Starting minimal server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
