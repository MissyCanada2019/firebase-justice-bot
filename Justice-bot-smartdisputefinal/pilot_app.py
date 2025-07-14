#!/usr/bin/env python3
"""
SmartDispute.ai Pilot Program - Clean Professional Platform
1000 free user accounts with instant signup
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pilot-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL not found")
    sys.exit(1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
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

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    return '''<!DOCTYPE html>
<html><head><title>SmartDispute.ai</title><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif}
.hero{color:white;text-align:center;padding:60px 0}
.hero h1{font-size:3rem;font-weight:700;margin-bottom:20px}
.card{background:rgba(255,255,255,0.95);border:none;border-radius:15px;box-shadow:0 20px 40px rgba(0,0,0,0.2)}
.auth-btn{width:100%;padding:15px;border:none;background:#4285f4;color:white;border-radius:8px;font-size:1.1rem;font-weight:600;cursor:pointer}
.auth-btn:hover{background:#3367d6}
.badge{background:#007bff;color:white;padding:6px 12px;border-radius:15px;font-size:0.8rem}
</style></head>
<body><div class="hero"><div class="container">
<div class="badge mb-3">Free Pilot Program</div>
<h1>SmartDispute.ai</h1>
<p class="lead">Professional Legal Platform</p>
<div class="row justify-content-center mt-4">
<div class="col-md-5"><div class="card"><div class="card-body p-4">
<h4 class="mb-3">Create Free Account</h4>
<p class="mb-3">Join our pilot program - 1000 free accounts available</p>
<button onclick="createAccount()" class="auth-btn" id="signupBtn">Sign Up with Google</button>
<div id="status" class="mt-3"></div>
<div class="text-center mt-3"><small class="text-muted">Free access for first 1000 users</small></div>
</div></div></div></div></div></div>
<script type="module">
import{initializeApp}from"https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js";
import{getAuth,GoogleAuthProvider,signInWithPopup}from"https://www.gstatic.com/firebasejs/9.22.0/firebase-auth.js";
const firebaseConfig={apiKey:"AIzaSyCoQVVf5g_3nkK4vZKKE6_q6jQJL1TdFvM",authDomain:"legallysmart-5a59c.firebaseapp.com",projectId:"legallysmart-5a59c"};
const app=initializeApp(firebaseConfig);const auth=getAuth(app);const provider=new GoogleAuthProvider();
window.createAccount=async function(){
const btn=document.getElementById("signupBtn");const status=document.getElementById("status");
btn.disabled=true;btn.textContent="Creating...";
try{const result=await signInWithPopup(auth,provider);const idToken=await result.user.getIdToken();
const response=await fetch("/signup",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({idToken:idToken})});
const data=await response.json();
if(response.ok&&data.success){status.innerHTML='<div class="text-success">Success! Redirecting...</div>';
setTimeout(()=>{window.location.href="/dashboard";},1000);}else{throw new Error(data.error||"Signup failed");}}
catch(error){status.innerHTML='<div class="text-danger">Error: '+error.message+"</div>";
btn.disabled=false;btn.textContent="Sign Up with Google";}};
</script></body></html>'''

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'success': False, 'error': 'Token required'}), 400
        
        # Verify token
        verify_url = "https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyCoQVVf5g_3nkK4vZKKE6_q6jQJL1TdFvM"
        response = requests.post(verify_url, json={"idToken": id_token}, timeout=10)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'Auth failed'}), 401
        
        user_data = response.json()['users'][0]
        email = user_data.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email required'}), 400
        
        # Check capacity
        current_users = User.query.count()
        if current_users >= 1000:
            return jsonify({'success': False, 'error': 'Pilot full (1000 users)'}), 400
        
        # Create or get user
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
            logger.info(f"New pilot user: {email} (Total: {current_users + 1}/1000)")
        
        login_user(user, remember=True)
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'email': user.email
        })
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'success': False, 'error': 'Account creation failed'}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    total_users = User.query.count()
    return f'''<!DOCTYPE html>
<html><head><title>Dashboard - SmartDispute.ai</title><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif}}
.hero{{color:white;text-align:center;padding:40px 0}}
.card{{background:rgba(255,255,255,0.95);border:none;border-radius:15px;box-shadow:0 20px 40px rgba(0,0,0,0.2)}}
.badge{{background:#007bff;color:white;padding:6px 12px;border-radius:15px;font-size:0.8rem;margin-bottom:20px;display:inline-block}}
.btn-action{{background:#667eea;border:none;border-radius:8px;padding:10px 20px;color:white;text-decoration:none;margin:5px;display:inline-block}}
.btn-logout{{background:#dc3545;border:none;border-radius:8px;padding:10px 20px;color:white;text-decoration:none;margin:5px;display:inline-block}}
</style></head>
<body><div class="hero"><div class="container">
<div class="badge">Free Pilot Account</div>
<h1>Welcome to SmartDispute.ai</h1></div></div>
<div class="container"><div class="row justify-content-center">
<div class="col-md-8"><div class="card"><div class="card-body p-4">
<h3>Account Active</h3><hr>
<div class="row"><div class="col-md-6">
<h5>Account Details</h5>
<p><strong>Name:</strong> {current_user.first_name or 'Not set'} {current_user.last_name or ''}</p>
<p><strong>Email:</strong> {current_user.email}</p>
<p><strong>Account ID:</strong> {current_user.id}</p>
<p><strong>Status:</strong> Free Pilot User</p>
<p><strong>Joined:</strong> {current_user.created_at.strftime('%B %d, %Y')}</p>
</div><div class="col-md-6">
<h5>Pilot Program</h5>
<p><strong>Users:</strong> {total_users}/1000</p>
<p><strong>Access:</strong> Full Platform</p>
<div class="progress mt-2" style="height:8px">
<div class="progress-bar bg-primary" style="width:{(total_users/1000)*100}%"></div></div>
<small class="text-muted">Pilot capacity</small>
</div></div><hr>
<h4>Platform Ready</h4>
<p>Your free account provides full access to all features.</p>
<div class="text-center mt-3">
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

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            user_count = User.query.count()
            logger.info(f"SmartDispute.ai pilot ready - {user_count}/1000 users")
        except Exception as e:
            logger.error(f"Database error: {e}")
            sys.exit(1)
    
    logger.info("Starting SmartDispute.ai on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)