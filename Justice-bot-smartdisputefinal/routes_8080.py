#!/usr/bin/env python3
"""
SmartDispute.ai routes for port 8080 direct application

This file is a modified version of routes.py that works with the direct port 8080 application.
It imports the app object from direct_port8080.py instead of defining routes globally.
"""

# Import the Flask app from our direct port 8080 module
import logging
from flask import render_template, jsonify
from direct_port8080 import app, db, logger

# Import route handlers from the original routes.py
from routes import *

# Define a simple index route if not already defined
@app.route('/')
def index():
    """Main index route"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return render_template('error.html', error=str(e))

# Define a basic port detection route for debugging
@app.route('/port')
def show_port():
    """Show which port the app is running on"""
    return jsonify({"port": 8080, "status": "ok"}), 200
