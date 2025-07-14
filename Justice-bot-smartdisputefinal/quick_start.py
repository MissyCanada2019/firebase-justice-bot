#!/usr/bin/env python3
"""
Quick start script for SmartDispute.ai
Minimal configuration to get the app running immediately
"""

import os
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

db = SQLAlchemy(app, model_class=Base)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    firebase_uid = db.Column(db.String(255), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SmartDispute.ai</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .card { 
            background: rgba(255,255,255,0.95); 
            backdrop-filter: blur(10px);
            border: none; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border: none; 
            border-radius: 50px;
            padding: 12px 30px;
        }
        .hero { color: white; text-align: center; padding: 80px 0; }
        .hero h1 { font-size: 3rem; font-weight: 700; margin-bottom: 20px; }
        .auth-btn { 
            width: 100%; 
            margin-bottom: 15px; 
            padding: 15px; 
            border: 2px solid #e0e0e0; 
            background: white; 
            border-radius: 10px; 
        }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1>SmartDispute.ai</h1>
            <p class="lead">AI-Powered Legal Platform</p>
            
            {% if current_user.is_authenticated %}
                <div class="row justify-content-center mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body p-4">
                                <h4>Welcome, {{ current_user.first_name or current_user.email }}!</h4>
                                <p class="mb-3">Account created: {{ current_user.created_at.strftime('%B %d, %Y') }}</p>
                                <a href="/dashboard" class="btn btn-primary me-2">Dashboard</a>
                                <a href="/logout" class="btn btn-outline-primary">Logout</a>
                            </div>
                        </div>
                    </div>
                </div>
            {% else %}
                <div class="row justify-content-center mt-4">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body p-4">
                                <h5 class="mb-3">Get Started</h5>
                                <button onclick="signInWithGoogle()" class="auth-btn">
                                    🔵 Continue with Google
                                </button>
                                <button class="auth-btn" disabled>
                                    📘 Continue with Facebook (Coming Soon)
                                </button>
                                <button class="auth-btn" disabled>
                                    🐦 Continue with Twitter (Coming Soon)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            {% endif %}
        </div>
    </div>

    <script type="module">
        import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js';
        import { getAuth, GoogleAuthProvider, signInWithPopup } from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-auth.js';

        const firebaseConfig = {
            apiKey: "AIzaSyCoQVVf5g_3nkK4vZKKE6_q6jQJL1TdFvM",
            authDomain: "legallysmart-5a59c.firebaseapp.com",
            projectId: "legallysmart-5a59c"
        };

        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const provider = new GoogleAuthProvider();

        window.signInWithGoogle = async function() {
            try {
                const result = await signInWithPopup(auth, provider);
                const idToken = await result.user.getIdToken();
                
                const response = await fetch('/firebase_login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ idToken: idToken })
                });
                
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert('Login failed. Please try again.');
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Login failed: ' + error.message);
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HOME_TEMPLATE)

@app.route('/dashboard')
@login_required
def dashboard():
    return f'''
    <div style="padding: 50px; font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white;">
        <div style="max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.95); color: #333; padding: 40px; border-radius: 15px;">
            <h1>SmartDispute.ai Dashboard</h1>
            <p><strong>Welcome back, {current_user.first_name or current_user.email}!</strong></p>
            <p>Account ID: {current_user.id}</p>
            <p>Email: {current_user.email}</p>
            <p>Created: {current_user.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
            <hr>
            <h3>Quick Actions</h3>
            <p><a href="/upload" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Upload Documents</a></p>
            <p><a href="/logout" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Logout</a></p>
        </div>
    </div>
    '''

@app.route('/firebase_login', methods=['POST'])
def firebase_login():
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No token'}), 400
        
        # Verify with Firebase
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyCoQVVf5g_3nkK4vZKKE6_q6jQJL1TdFvM"
        response = requests.post(verify_url, json={"idToken": id_token})
        
        if response.status_code != 200:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_data = response.json()['users'][0]
        email = user_data.get('email')
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User()
            user.email = email
            user.firebase_uid = user_data.get('localId')
            if user_data.get('displayName'):
                name_parts = user_data['displayName'].split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created user: {email}")
        
        login_user(user, remember=True)
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Login error: {e}")
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
        return jsonify({'status': 'healthy', 'users': user_count})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Database ready")
    
    print("SmartDispute.ai starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)