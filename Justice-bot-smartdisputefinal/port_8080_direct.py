#!/usr/bin/env python3
"""
Direct port 8080 server for Replit web interface compatibility
Runs the complete SmartDispute.ai application on port 8080
"""

import os
import sys
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-testing")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# CSRF Protection with enhanced domain handling
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow both HTTP and HTTPS
app.config['WTF_CSRF_CHECK_DEFAULT'] = True

# Initialize database
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Import and register routes
with app.app_context():
    try:
        # Import models first
        import models
        
        # Create tables
        db.create_all()
        
        # Import and register all routes
        from routes import register_routes
        register_routes(app)
        
        logger.info("Application initialized successfully on port 8080")
        
    except Exception as e:
        logger.error(f"Error initializing application: {e}")

@app.route('/health')
def health_check():
    return {"status": "ok", "port": 8080}

if __name__ == "__main__":
    port = 8080
    logger.info(f"Starting SmartDispute.ai on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)