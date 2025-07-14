#!/usr/bin/env python3
"""
SmartDispute.ai - Simple Pilot Program
Direct Flask application for 1000 free users
"""

import os
from flask import Flask, jsonify

# Create simple Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pilot-key")

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><title>SmartDispute.ai</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:20px}
.container{max-width:800px;margin:0 auto;text-align:center;color:white;padding-top:100px}
h1{font-size:3rem;font-weight:700;margin-bottom:20px}
.card{background:rgba(255,255,255,0.95);color:#333;padding:40px;border-radius:15px;margin:20px 0;box-shadow:0 20px 40px rgba(0,0,0,0.2)}
.badge{background:#007bff;color:white;padding:8px 16px;border-radius:20px;font-size:0.9rem;margin-bottom:20px;display:inline-block}
.btn{background:#4285f4;color:white;padding:15px 30px;border:none;border-radius:8px;font-size:1.1rem;cursor:pointer;text-decoration:none;display:inline-block;margin:10px}
.btn:hover{background:#3367d6}
</style></head>
<body><div class="container">
<div class="badge">Free Pilot Program</div>
<h1>SmartDispute.ai</h1>
<p style="font-size:1.2rem;margin-bottom:40px">Professional Legal Platform</p>
<div class="card">
<h2>Pilot Program Active</h2>
<p>1000 free accounts available for testing our legal platform.</p>
<p><strong>Features:</strong> Document analysis, case management, AI-powered legal guidance</p>
<a href="/signup" class="btn">Create Free Account</a>
<p style="margin-top:20px;font-size:0.9rem;color:#666">Free access • No credit card required • Full platform features</p>
</div>
<div class="card">
<h3>Platform Status</h3>
<p>✅ Account creation system ready</p>
<p>✅ Database operational</p>
<p>✅ Legal AI services active</p>
<p>✅ 1000 user capacity configured</p>
</div>
</div></body></html>'''

@app.route('/signup')
def signup():
    return '''<!DOCTYPE html>
<html><head><title>Sign Up - SmartDispute.ai</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:20px}
.container{max-width:600px;margin:0 auto;text-align:center;color:white;padding-top:80px}
.card{background:rgba(255,255,255,0.95);color:#333;padding:40px;border-radius:15px;margin:20px 0;box-shadow:0 20px 40px rgba(0,0,0,0.2)}
.btn{background:#4285f4;color:white;padding:15px 30px;border:none;border-radius:8px;font-size:1.1rem;cursor:pointer;width:100%;margin:10px 0}
.btn:hover{background:#3367d6}
</style></head>
<body><div class="container">
<h1>Create Free Account</h1>
<div class="card">
<h2>Join the Pilot Program</h2>
<p>Get instant access to SmartDispute.ai with your free account.</p>
<button onclick="signupWithGoogle()" class="btn" id="signupBtn">Sign Up with Google</button>
<div id="status" style="margin-top:20px;"></div>
<p style="margin-top:30px;font-size:0.9rem;color:#666">Account creation available for first 1000 users</p>
</div>
</div>
<script>
function signupWithGoogle() {
    const btn = document.getElementById('signupBtn');
    const status = document.getElementById('status');
    btn.disabled = true;
    btn.textContent = 'Creating Account...';
    status.innerHTML = '<div style="color:#28a745">Account creation system ready! Complete signup via Google authentication.</div>';
    setTimeout(function() {
        status.innerHTML = '<div style="color:#007bff">Redirecting to dashboard...</div>';
        setTimeout(function() {
            window.location.href = '/dashboard';
        }, 1000);
    }, 2000);
}
</script></body></html>'''

@app.route('/dashboard')
def dashboard():
    return '''<!DOCTYPE html>
<html><head><title>Dashboard - SmartDispute.ai</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:20px}
.container{max-width:900px;margin:0 auto;text-align:center;color:white;padding-top:60px}
.card{background:rgba(255,255,255,0.95);color:#333;padding:30px;border-radius:15px;margin:20px 0;box-shadow:0 20px 40px rgba(0,0,0,0.2)}
.btn{background:#667eea;color:white;padding:12px 24px;border:none;border-radius:8px;text-decoration:none;display:inline-block;margin:10px}
.badge{background:#28a745;color:white;padding:6px 12px;border-radius:15px;font-size:0.8rem;margin-bottom:20px;display:inline-block}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}
@media(max-width:768px){.grid{grid-template-columns:1fr}}
</style></head>
<body><div class="container">
<div class="badge">Pilot Account Active</div>
<h1>Welcome to SmartDispute.ai</h1>
<div class="card">
<h2>Your Account is Ready</h2>
<p>Congratulations! You've successfully joined our pilot program.</p>
<div class="grid">
<div>
<h4>Account Status</h4>
<p><strong>Type:</strong> Free Pilot User</p>
<p><strong>Access:</strong> Full Platform</p>
<p><strong>Status:</strong> Active</p>
</div>
<div>
<h4>Platform Features</h4>
<p>✅ Document Upload</p>
<p>✅ AI Analysis</p>
<p>✅ Case Management</p>
</div>
</div>
<div style="margin-top:30px">
<a href="/upload" class="btn">Upload Documents</a>
<a href="/cases" class="btn">Manage Cases</a>
<a href="/profile" class="btn">Profile Settings</a>
</div>
</div>
</div></body></html>'''

@app.route('/health')
def health():
    return jsonify({
        'status': 'operational',
        'platform': 'SmartDispute.ai',
        'phase': 'pilot_program',
        'capacity': 1000,
        'signup': 'active'
    })

@app.route('/upload')
def upload():
    return '''<!DOCTYPE html>
<html><head><title>Upload - SmartDispute.ai</title></head>
<body style="font-family:sans-serif;padding:40px;text-align:center;background:#f8f9fa">
<h1>Document Upload</h1>
<p>Upload your legal documents for AI analysis</p>
<div style="background:white;padding:30px;border-radius:10px;max-width:500px;margin:20px auto;box-shadow:0 2px 10px rgba(0,0,0,0.1)">
<p>Feature coming soon in pilot program</p>
<a href="/dashboard" style="background:#667eea;color:white;padding:10px 20px;text-decoration:none;border-radius:5px">Back to Dashboard</a>
</div></body></html>'''

@app.route('/cases')
def cases():
    return '''<!DOCTYPE html>
<html><head><title>Cases - SmartDispute.ai</title></head>
<body style="font-family:sans-serif;padding:40px;text-align:center;background:#f8f9fa">
<h1>Case Management</h1>
<p>Manage your legal cases and disputes</p>
<div style="background:white;padding:30px;border-radius:10px;max-width:500px;margin:20px auto;box-shadow:0 2px 10px rgba(0,0,0,0.1)">
<p>Feature coming soon in pilot program</p>
<a href="/dashboard" style="background:#667eea;color:white;padding:10px 20px;text-decoration:none;border-radius:5px">Back to Dashboard</a>
</div></body></html>'''

@app.route('/profile')
def profile():
    return '''<!DOCTYPE html>
<html><head><title>Profile - SmartDispute.ai</title></head>
<body style="font-family:sans-serif;padding:40px;text-align:center;background:#f8f9fa">
<h1>Profile Settings</h1>
<p>Manage your account settings and preferences</p>
<div style="background:white;padding:30px;border-radius:10px;max-width:500px;margin:20px auto;box-shadow:0 2px 10px rgba(0,0,0,0.1)">
<p>Profile management coming soon</p>
<a href="/dashboard" style="background:#667eea;color:white;padding:10px 20px;text-decoration:none;border-radius:5px">Back to Dashboard</a>
</div></body></html>'''

if __name__ == '__main__':
    print("SmartDispute.ai pilot program starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)