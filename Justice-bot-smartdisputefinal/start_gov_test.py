#!/usr/bin/env python3
"""
SmartDispute.ai - Free Account Creation Platform
1000 user pilot program with instant account setup
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "gov-test-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set")
    sys.exit(1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
    "pool_timeout": 20,
}

# Initialize extensions
db = SQLAlchemy(app, model_class=Base)
login_manager = LoginManager()
login_manager.init_app(app)

# User model for government testing
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    firebase_uid = db.Column(db.String(255), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_free_user = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Homepage with account creation
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    return '''<!DOCTYPE html>
<html><head><title>SmartDispute.ai - Legal Platform</title><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif}
.card{background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);border:none;border-radius:15px;box-shadow:0 20px 40px rgba(0,0,0,0.2)}
.hero{color:white;text-align:center;padding:80px 0}
.hero h1{font-size:3.5rem;font-weight:700;margin-bottom:20px;text-shadow:0 2px 10px rgba(0,0,0,0.3)}
.auth-btn{width:100%;margin-bottom:20px;padding:20px;border:none;background:linear-gradient(135deg,#4285f4 0%,#34a853 100%);color:white;border-radius:10px;font-size:1.2rem;font-weight:600}
.status-badge{background:#007bff;color:white;padding:8px 16px;border-radius:20px;font-size:0.9rem;margin-bottom:20px;display:inline-block}
</style></head>
<body><div class="hero"><div class="container"><h1>SmartDispute.ai</h1><p class="lead">AI-Powered Legal Platform</p>
<div class="status-badge">Free Pilot Program</div>
<div class="row justify-content-center mt-5"><div class="col-md-5"><div class="card"><div class="card-body p-5">
<h3 class="mb-4">Create Your Free Account</h3>
<p class="mb-4">Join our pilot program with 1000 free accounts available.</p>
<button onclick="createAccount()" class="auth-btn" id="createBtn">Create Free Account with Google</button>
<div id="status" class="mt-3"></div>
<div class="text-center mt-4"><small class="text-muted">Free access for first 1000 users</small></div>
</div></div></div></div></div></div>
<script type="module">
import{initializeApp}from"https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js";
import{getAuth,GoogleAuthProvider,signInWithPopup}from"https://www.gstatic.com/firebasejs/9.22.0/firebase-auth.js";
const firebaseConfig={apiKey:"AIzaSyCoQVVf5g_3nkK4vZKKE6_q6jQJL1TdFvM",authDomain:"legallysmart-5a59c.firebaseapp.com",projectId:"legallysmart-5a59c"};
const app=initializeApp(firebaseConfig);const auth=getAuth(app);const provider=new GoogleAuthProvider();
window.createAccount=async function(){
const btn=document.getElementById("createBtn");const status=document.getElementById("status");
btn.disabled=true;btn.textContent="Creating Account...";status.innerHTML='<div class="text-info">Authenticating...</div>';
try{const result=await signInWithPopup(auth,provider);const idToken=await result.user.getIdToken();
status.innerHTML='<div class="text-info">Setting up your account...</div>';
const response=await fetch("/signup",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({idToken:idToken})});
const data=await response.json();
if(response.ok&&data.success){status.innerHTML='<div class="text-success">Account created! Redirecting...</div>';
setTimeout(()=>{window.location.href="/dashboard";},1000);}else{throw new Error(data.error||"Account creation failed");}}
catch(error){console.error("Error:",error);status.innerHTML='<div class="text-danger">Error: '+error.message+"</div>";
btn.disabled=false;btn.textContent="Create Free Account with Google";}};
</script></body></html>'''

# Account creation endpoint
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 400
        
        # Verify Firebase token
        verify_url = "https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyCoQVVf5g_3nkK4vZKKE6_q6jQJL1TdFvM"
        response = requests.post(verify_url, json={"idToken": id_token}, timeout=15)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'Authentication failed'}), 401
        
        user_data = response.json()['users'][0]
        email = user_data.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email required'}), 400
        
        # Check pilot program capacity
        current_users = User.query.count()
        if current_users >= 1000:
            return jsonify({'success': False, 'error': 'Pilot program full (1000 users)'}), 400
        
        # Create or find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User()
            user.email = email
            user.firebase_uid = user_data.get('localId')
            user.is_free_user = True
            
            if user_data.get('displayName'):
                name_parts = user_data['displayName'].split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Pilot user created: {email} (ID: {user.id}, Total: {current_users + 1}/1000)")
        
        # Log user in
        login_user(user, remember=True)
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'email': user.email
        })
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'success': False, 'error': 'Account creation failed'}), 500

# Dashboard for logged-in users
@app.route('/dashboard')
@login_required
def dashboard():
    total_users = User.query.count()
    return f'''<!DOCTYPE html>
<html><head><title>SmartDispute.ai Dashboard</title><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif}}
.card{{background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);border:none;border-radius:15px;box-shadow:0 20px 40px rgba(0,0,0,0.2)}}
.hero{{color:white;text-align:center;padding:40px 0}}
.status-badge{{background:#007bff;color:white;padding:8px 16px;border-radius:20px;font-size:0.9rem;margin-bottom:20px;display:inline-block}}
.btn-action{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border:none;border-radius:10px;padding:12px 24px;color:white;text-decoration:none;margin:5px;display:inline-block;font-weight:600}}
.btn-logout{{background:#dc3545;border:none;border-radius:10px;padding:12px 24px;color:white;text-decoration:none;margin:5px;display:inline-block}}
</style></head>
<body><div class="hero"><div class="container"><div class="status-badge">Free Pilot Account Active</div>
<h1>Welcome to SmartDispute.ai</h1></div></div>
<div class="container"><div class="row justify-content-center"><div class="col-md-8"><div class="card"><div class="card-body p-5">
<h2>Account Successfully Created</h2><hr>
<div class="row"><div class="col-md-6">
<h5>Account Details</h5>
<p><strong>Name:</strong> {current_user.first_name or 'Not provided'} {current_user.last_name or ''}</p>
<p><strong>Email:</strong> {current_user.email}</p>
<p><strong>Account ID:</strong> {current_user.id}</p>
<p><strong>Status:</strong> Free Pilot Account</p>
<p><strong>Created:</strong> {current_user.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
</div><div class="col-md-6">
<h5>Pilot Program Status</h5>
<p><strong>Registered Users:</strong> {total_users}/1000</p>
<p><strong>Access Level:</strong> Full Platform Access</p>
<div class="progress mt-3" style="height:10px">
<div class="progress-bar bg-primary" style="width:{(total_users/1000)*100}%"></div></div>
<small class="text-muted">Pilot program capacity</small>
</div></div><hr>
<h4>Platform Ready</h4>
<p>Your free account provides full access to SmartDispute.ai features.</p>
<div class="text-center mt-4">
<a href="/upload" class="btn-action">Upload Documents</a>
<a href="/cases" class="btn-action">Manage Cases</a>
<a href="/logout" class="btn-logout">Logout</a>
</div></div></div></div></div></div></body></html>'''

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
            'status': 'operational',
            'platform': 'SmartDispute.ai',
            'phase': 'pilot_program',
            'users': user_count,
            'capacity': 1000,
            'signup': 'active'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

def initialize_database():
    """Initialize database for government testing"""
    try:
        db.create_all()
        user_count = User.query.count()
        logger.info(f"Database initialized - {user_count} users registered for pilot program")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == '__main__':
    with app.app_context():
        if not initialize_database():
            sys.exit(1)
    
    logger.info("Starting SmartDispute.ai Pilot Program Platform on port 5000")
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)