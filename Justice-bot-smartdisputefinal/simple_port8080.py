#!/usr/bin/env python3
"""
Simple Port 8080 Server for SmartDispute.ai Access
"""

import http.server
import socketserver
import threading
import time

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_main_page()
        elif self.path == '/health':
            self.send_health()
        else:
            self.send_main_page()
    
    def send_main_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = '''<!DOCTYPE html>
<html><head><title>SmartDispute.ai</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:20px}
.container{max-width:800px;margin:0 auto;text-align:center;color:white;padding-top:100px}
h1{font-size:3rem;font-weight:700;margin-bottom:20px}
.card{background:rgba(255,255,255,0.95);color:#333;padding:40px;border-radius:15px;margin:20px 0;box-shadow:0 20px 40px rgba(0,0,0,0.2)}
.badge{background:#007bff;color:white;padding:8px 16px;border-radius:20px;font-size:0.9rem;margin-bottom:20px;display:inline-block}
.btn{background:#4285f4;color:white;padding:15px 30px;border:none;border-radius:8px;font-size:1.1rem;cursor:pointer;text-decoration:none;display:inline-block;margin:10px}
.btn:hover{background:#3367d6}
</style>
<script type="module">
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.9.1/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/11.9.1/firebase-auth.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.9.1/firebase-analytics.js";

const firebaseConfig = {
    apiKey: "AIzaSyAjd5ekT45EOPr7D-KvSZt-EPwaOk0BQUE",
    authDomain: "legallysmart.firebaseapp.com",
    projectId: "legallysmart",
    storageBucket: "legallysmart.firebasestorage.app",
    messagingSenderId: "1077200418820",
    appId: "1:1077200418820:web:aca47450b47ed258df1d51",
    measurementId: "G-3N4JD9CRXY"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = getAnalytics(app);
const provider = new GoogleAuthProvider();

window.signUp = async function() {
    const btn = document.getElementById('signupBtn');
    const status = document.getElementById('status');
    
    btn.disabled = true;
    btn.textContent = 'Authenticating...';
    
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        
        status.innerHTML = '<div style="color:#28a745;font-weight:bold">Authentication successful!</div>';
        btn.textContent = 'Redirecting...';
        
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
        
    } catch (error) {
        status.innerHTML = '<div style="color:#dc3545">Please try again</div>';
        btn.disabled = false;
        btn.textContent = 'Sign Up with Google';
    }
};
</script>
</head>
<body><div class="container">
<div class="badge">Free Pilot Program</div>
<h1>SmartDispute.ai</h1>
<p style="font-size:1.2rem;margin-bottom:40px">Professional Legal Platform</p>
<div class="card">
<h2>Join Our Pilot Program</h2>
<p>1000 free accounts available for our legal automation platform.</p>
<button onclick="signUp()" class="btn" id="signupBtn">Sign Up with Google</button>
<div id="status" style="margin-top:20px;"></div>
<p style="margin-top:20px;font-size:0.9rem;color:#666">Free access • No credit card required</p>
</div>
<div class="card">
<h3>Platform Features</h3>
<p>Document analysis • Case management • AI legal guidance</p>
<p>Built specifically for Canadian legal processes</p>
</div>
</div></body></html>'''
        
        self.wfile.write(html.encode())
    
    def send_health(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status":"ok","port":8080}')
    
    def log_message(self, format, *args):
        pass  # Disable logging

def start_port8080():
    """Start server on port 8080"""
    port = 8080
    handler = SimpleHandler
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
            print(f"Port 8080 server started")
            httpd.serve_forever()
    except Exception as e:
        print(f"Port 8080 error: {e}")
        time.sleep(5)
        start_port8080()  # Restart on error

if __name__ == "__main__":
    start_port8080()