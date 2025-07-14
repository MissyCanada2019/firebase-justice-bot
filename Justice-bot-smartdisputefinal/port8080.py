#!/usr/bin/env python3
"""
Simple port 8080 Flask application for SmartDispute.ai
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Core Flask imports
from flask import Flask, render_template, redirect, request, jsonify, url_for

# Create a basic Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

@app.route('/')
def index():
    """Basic index route"""
    logger.info("Serving index page on port 8080")
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "port": 8080,
        "service": "SmartDispute.ai Port 8080"
    })

# Run the application directly
if __name__ == "__main__":
    port = 8080
    logger.info(f"Starting simplified SmartDispute.ai on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
