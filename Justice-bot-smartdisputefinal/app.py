#!/usr/bin/env python3
"""
SmartDispute.ai - Canadian Legal Assistant Platform
Complete Flask application with authentication, document upload, and AI analysis
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from database_fix import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
login_manager = LoginManager()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # App configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///smartdispute.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    
    # File upload configuration
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    app.config["UPLOAD_FOLDER"] = "uploads"

    # Enable CORS for the app
    CORS(app)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.cases import cases_bp
    from routes.admin import admin_bp
    from security_blocks import security_bp
    
    # Register security blocks first (higher priority)
    app.register_blueprint(security_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(cases_bp, url_prefix='/cases')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Legal analyzer functionality is integrated into the cases blueprint
    # No separate module needed - all AI analysis happens in routes/cases.py
    
    # Create tables
    with app.app_context():
        import models  # Import models to register them
        db.create_all()
        logger.info("Database tables created successfully")
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(user_id)
    
    logger.info("SmartDispute.ai application created successfully")
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)