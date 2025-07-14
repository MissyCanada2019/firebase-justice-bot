#!/usr/bin/env python3
"""
Direct Port 8080 Application for SmartDispute.ai

This file is the main entry point for the application running directly on port 8080,
which is required for Replit web interface compatibility.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from flask import Flask, jsonify, render_template, request

# Create a simple Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

@app.route('/')
def index():
    """Main index route"""
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    logger.info("Health check request")
    return jsonify({
        "status": "ok",
        "port": 8080,
        "service": "SmartDispute.ai"
    })

@app.route('/port')
def port_info():
    """Show port information for debugging"""
    return jsonify({
        "running_on": 8080,
        "status": "Direct port 8080 access"
    })

if __name__ == "__main__":
    # Explicitly run on port 8080 which is required for Replit
    port = 8080
    logger.info(f"Starting SmartDispute.ai on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
