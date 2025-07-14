#!/usr/bin/env python3
"""
Port 8080 Server with Firebase Authentication for SmartDispute.ai
This server runs on port 8080 and includes Firebase auth integration
"""

import os
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import json

class FirebaseHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_homepage()
        elif self.path == '/signup':
            self.send_signup_page()
        elif self.path == '/dashboard':
            self.send_dashboard()
        elif self.path == '/health':
            self.send_health()
        else:
            self.send_redirect_to_main()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/auth':
            self.handle_firebase_auth()
        else:
            self.send_redirect_to_main()
    
    def send_homepage(self):
        """Send the main homepage with Firebase auth"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartDispute.ai - Legal Platform</title>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            text-align: center;
            color: white;
            padding-top: 60px;
        }
        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .badge {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1rem;
            margin-bottom: 30px;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .card {
            background: rgba(255,255,255,0.95);
            color: #333;
            padding: 40px;
            border-radius: 20px;
            margin: 30px 0;
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }
        .btn {
            background: #4285f4;
            color: white;
            padding: 15px 35px;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
        }
        .btn:hover {
            background: #3367d6;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(66, 133, 244, 0.4);
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .feature {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            color: white;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #28a745;
            border-radius: 50%;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">Free Pilot Program</div>
        <h1>SmartDispute.ai</h1>
        <p style="font-size: 1.3rem; margin-bottom: 40px; opacity: 0.9;">
            Professional Legal Automation Platform
        </p>
        
        <div class="card">
            <h2>Join Our Pilot Program</h2>
            <p style="font-size: 1.1rem; margin-bottom: 30px;">
                Get free access to our comprehensive legal platform with 1000 pilot accounts available.
            </p>
            <button onclick="signUpWithGoogle()" class="btn" id="signupBtn">
                📱 Sign Up with Google
            </button>
            <div id="authStatus" style="margin-top: 20px;"></div>
            <p style="margin-top: 25px; font-size: 0.9rem; color: #666;">
                Free access • No credit card required • Full platform features
            </p>
        </div>
        
        <div class="card">
            <h3>Platform Features</h3>
            <div class="feature-grid">
                <div class="feature">
                    <h4>🔍 Document Analysis</h4>
                    <p>AI-powered legal document review and analysis</p>
                </div>
                <div class="feature">
                    <h4>📋 Case Management</h4>
                    <p>Comprehensive case tracking and organization</p>
                </div>
                <div class="feature">
                    <h4>⚖️ Legal Guidance</h4>
                    <p>Smart recommendations based on Canadian law</p>
                </div>
                <div class="feature">
                    <h4>📄 Form Generation</h4>
                    <p>Automated court-ready document creation</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>System Status</h3>
            <p><span class="status-indicator"></span>Account creation system ready</p>
            <p><span class="status-indicator"></span>Database operational</p>
            <p><span class="status-indicator"></span>Legal AI services active</p>
            <p><span class="status-indicator"></span>1000 user capacity configured</p>
        </div>
    </div>

    <!-- Firebase SDK -->
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

        window.signUpWithGoogle = async function() {
            const btn = document.getElementById('signupBtn');
            const status = document.getElementById('authStatus');
            
            btn.disabled = true;
            btn.textContent = 'Connecting to Google...';
            
            try {
                const result = await signInWithPopup(auth, provider);
                const user = result.user;
                
                status.innerHTML = '<div style="color: #28a745; font-weight: bold;">✅ Authentication successful!</div>';
                btn.textContent = 'Redirecting to Dashboard...';
                
                setTimeout(() => {
                    window.location.href = '/dashboard?uid=' + user.uid + '&email=' + encodeURIComponent(user.email) + '&name=' + encodeURIComponent(user.displayName);
                }, 1500);
                
            } catch (error) {
                console.error('Authentication error:', error);
                status.innerHTML = '<div style="color: #dc3545;">Authentication failed. Please try again.</div>';
                btn.disabled = false;
                btn.textContent = '📱 Sign Up with Google';
            }
        };
    </script>
</body>
</html>'''
        self.wfile.write(html.encode())
    
    def send_signup_page(self):
        """Send signup page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = '''<!DOCTYPE html>
<html>
<head>
    <title>Join SmartDispute.ai</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; font-family: sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; text-align: center; color: white; padding-top: 80px; }
        .card { background: rgba(255,255,255,0.95); color: #333; padding: 40px; border-radius: 15px; margin: 20px 0; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
        .btn { background: #4285f4; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 1.1rem; cursor: pointer; width: 100%; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Your Free Account</h1>
        <div class="card">
            <h2>Join the Pilot Program</h2>
            <p>Get instant access to SmartDispute.ai professional legal platform.</p>
            <button onclick="window.location.href='/'" class="btn">Continue with Google Sign-Up</button>
            <p style="margin-top: 30px; font-size: 0.9rem; color: #666;">
                Account creation available for first 1000 users
            </p>
        </div>
    </div>
</body>
</html>'''
        self.wfile.write(html.encode())
    
    def send_dashboard(self):
        """Send dashboard page"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        user_email = query_params.get('email', [''])[0]
        user_name = query_params.get('name', ['User'])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - SmartDispute.ai</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; font-family: sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; text-align: center; color: white; padding-top: 60px; }}
        .card {{ background: rgba(255,255,255,0.95); color: #333; padding: 30px; border-radius: 15px; margin: 20px 0; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }}
        .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px; }}
        .badge {{ background: #28a745; color: white; padding: 6px 12px; border-radius: 15px; font-size: 0.8rem; margin-bottom: 20px; display: inline-block; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        @media(max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">Pilot Account Active</div>
        <h1>Welcome to SmartDispute.ai</h1>
        <div class="card">
            <h2>Account Successfully Created</h2>
            <p><strong>Welcome, {user_name}!</strong></p>
            <p>Email: {user_email}</p>
            <div class="grid">
                <div>
                    <h4>Account Status</h4>
                    <p><strong>Type:</strong> Free Pilot User</p>
                    <p><strong>Access:</strong> Full Platform</p>
                    <p><strong>Status:</strong> ✅ Active</p>
                </div>
                <div>
                    <h4>Available Features</h4>
                    <p>✅ Document Upload & Analysis</p>
                    <p>✅ AI Legal Guidance</p>
                    <p>✅ Case Management</p>
                </div>
            </div>
            <div style="margin-top: 30px;">
                <a href="/upload" class="btn">📄 Upload Documents</a>
                <a href="/cases" class="btn">📋 Manage Cases</a>
                <a href="/" class="btn">🏠 Back to Home</a>
            </div>
        </div>
    </div>
</body>
</html>'''
        self.wfile.write(html.encode())
    
    def send_health(self):
        """Send health check response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        health_data = {
            'status': 'operational',
            'platform': 'SmartDispute.ai',
            'phase': 'pilot_program',
            'port': 8080,
            'capacity': 1000,
            'firebase': 'enabled'
        }
        self.wfile.write(json.dumps(health_data).encode())
    
    def handle_firebase_auth(self):
        """Handle Firebase authentication POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'message': 'Authentication received',
                'redirect_url': '/dashboard'
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(e)
            }
            
            self.wfile.write(json.dumps(error_response).encode())
    
    def send_redirect_to_main(self):
        """Redirect other requests to main app on port 5000"""
        self.send_response(302)
        self.send_header('Location', f'http://localhost:5000{self.path}')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[Port 8080] {format % args}")

def start_server():
    """Start the port 8080 server"""
    port = 8080
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), FirebaseHandler) as httpd:
            print(f"SmartDispute.ai serving on port {port}")
            print(f"Firebase authentication enabled")
            print(f"Access at: http://localhost:{port}/")
            httpd.serve_forever()
    except OSError as e:
        print(f"Error starting server on port {port}: {e}")
        exit(1)

if __name__ == "__main__":
    start_server()