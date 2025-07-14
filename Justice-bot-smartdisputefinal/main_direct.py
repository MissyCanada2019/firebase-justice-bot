#!/usr/bin/env python3
"""
Direct port 8080 application for SmartDispute.ai

This script runs the Flask application directly on port 8080 which is required by Replit
"""

import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize the database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Setup database tables
with app.app_context():
    import models  # This imports the model definitions
    db.create_all()

# Import routes after the app is initialized
import routes

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Run the application on port 8080 for Replit compatibility
    app.run(host="0.0.0.0", port=8080, debug=True)
