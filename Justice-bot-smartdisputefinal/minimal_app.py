#!/usr/bin/env python3
"""
Minimal working version of SmartDispute.ai
Focused on getting authentication working properly
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Initialize extensions
db = SQLAlchemy(app, model_class=Base)
login_manager = LoginManager()
login_manager.init_app(app)

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    firebase_uid = db.Column(db.String(255), nullable=True, unique=True)
    profile_image_url = db.Column(db.String, nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Firebase configuration
FIREBASE_CONFIG = {
    'apiKey': "AIzaSyCoQVVf5g_3nkK4vZKKE6_q6jQJL1TdFvM",
    'authDomain': "legallysmart-5a59c.firebaseapp.com",
    'projectId': "legallysmart-5a59c"
}

def verify_firebase_token(id_token):
    """Verify Firebase ID token"""
    try:
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_CONFIG['apiKey']}"
        
        payload = {"idToken": id_token}
        response = requests.post(verify_url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if 'users' in data and len(data['users']) > 0:
                user_data = data['users'][0]
                return {
                    'uid': user_data.get('localId'),
                    'email': user_data.get('email'),
                    'name': user_data.get('displayName'),
                    'photo_url': user_data.get('photoUrl'),
                    'email_verified': user_data.get('emailVerified', False)
                }
        return None
    except Exception as e:
        logger.error(f"Firebase token verification error: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"""
    <h1>Welcome to SmartDispute.ai Dashboard</h1>
    <p>Hello {current_user.first_name or current_user.email}!</p>
    <p>Account created: {current_user.created_at}</p>
    <a href="/logout">Logout</a>
    """

@app.route('/firebase_login', methods=['POST'])
def firebase_login():
    """Handle Firebase authentication"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No ID token provided'}), 400
        
        # Verify Firebase token
        firebase_user_data = verify_firebase_token(id_token)
        
        if not firebase_user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Find or create user
        user = User.query.filter_by(email=firebase_user_data['email']).first()
        
        if not user:
            user = User()
            user.email = firebase_user_data['email']
            user.firebase_uid = firebase_user_data['uid']
            if firebase_user_data.get('name'):
                name_parts = firebase_user_data['name'].split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.profile_image_url = firebase_user_data.get('photo_url')
            user.email_verified = firebase_user_data.get('email_verified', False)
            
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {user.email}")
        else:
            logger.info(f"Existing user logged in: {user.email}")
        
        # Log user in
        login_user(user, remember=True)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip()
            }
        })
        
    except Exception as e:
        logger.error(f"Firebase login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/health')
def health():
    try:
        user_count = User.query.count()
        return jsonify({
            'status': 'healthy',
            'users': user_count,
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database error: {e}")
    
    print("Starting SmartDispute.ai on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)