#!/usr/bin/env python3
"""
Justice-Bot - Simplified startup for debugging
"""

import os
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

class Base(DeclarativeBase):
    pass

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# Initialize extensions
db = SQLAlchemy(app, model_class=Base)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # For now, return None to avoid database queries
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return "OK", 200

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html', user=current_user, stats={
        'total_cases': 0,
        'analyzed_cases': 0,
        'generated_docs': 0,
        'completion_rate': 0
    }, cases=[])

# Create database tables
with app.app_context():
    db.create_all()
    print("Justice-Bot database initialized")

if __name__ == '__main__':
    print("Starting Justice-Bot Canadian Legal Assistant...")
    app.run(host='0.0.0.0', port=5000, debug=True)