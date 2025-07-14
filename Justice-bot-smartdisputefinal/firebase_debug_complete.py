#!/usr/bin/env python3
"""
Complete Firebase Debug and Fix Tool for SmartDispute.ai
Analyzes authentication issues and provides solutions
"""

import os
import sys
import requests
import json
import logging
import time
from datetime import datetime
from flask import Flask, jsonify, request
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAjd5ekT45EOPr7D-KvSZt-EPwaOk0BQUE",
    "authDomain": "legallysmart.firebaseapp.com",
    "projectId": "legallysmart",
    "storageBucket": "legallysmart.firebasestorage.app",
    "messagingSenderId": "1077200418820",
    "appId": "1:1077200418820:web:aca47450b47ed258df1d51",
    "measurementId": "G-3N4JD9CRXY"
}

def analyze_token_format(token):
    """Analyze the format of the provided token"""
    print("=" * 60)
    print("TOKEN ANALYSIS")
    print("=" * 60)
    
    print(f"Token: {token}")
    print(f"Length: {len(token)} characters")
    
    # Check if it looks like a UUID
    if len(token) == 36 and token.count('-') == 4:
        print("Format: UUID (not a Firebase ID token)")
        print("Issue: This appears to be a UUID, not a Firebase authentication token")
        print("Firebase ID tokens are much longer (typically 800-2000+ characters)")
        return "uuid"
    
    # Check if it looks like a Firebase ID token
    elif len(token) > 500 and '.' in token:
        print("Format: Likely Firebase ID token (JWT)")
        parts = token.split('.')
        print(f"JWT parts: {len(parts)} (should be 3)")
        return "jwt"
    
    else:
        print("Format: Unknown token format")
        print("Issue: This doesn't match expected Firebase ID token format")
        return "unknown"

def test_firebase_services():
    """Test Firebase service availability"""
    print("\n" + "=" * 60)
    print("FIREBASE SERVICES TEST")
    print("=" * 60)
    
    services = {
        "Identity Toolkit": f"https://identitytoolkit.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}",
        "Secure Token": f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_CONFIG['apiKey']}",
        "Auth Domain": f"https://{FIREBASE_CONFIG['authDomain']}",
        "Auth Handler": f"https://{FIREBASE_CONFIG['authDomain']}/__/auth/handler"
    }
    
    results = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            status = "✓ Available" if response.status_code in [200, 404] else f"✗ Error {response.status_code}"
            results[name] = response.status_code
            print(f"{name}: {status}")
        except Exception as e:
            results[name] = f"Error: {e}"
            print(f"{name}: ✗ {e}")
    
    return results

def create_test_firebase_app():
    """Create a test Flask app with Firebase endpoints"""
    app = Flask(__name__)
    app.secret_key = 'test-key-for-debugging'
    
    @app.route('/auth/config')
    def firebase_config():
        return jsonify(FIREBASE_CONFIG)
    
    @app.route('/auth/test-token', methods=['POST'])
    def test_token():
        data = request.get_json()
        token = data.get('token', '')
        
        # Simulate token verification
        if len(token) > 500:  # Proper Firebase token length
            return jsonify({'valid': True, 'message': 'Token format appears valid'})
        else:
            return jsonify({'valid': False, 'message': 'Token too short for Firebase ID token'})
    
    @app.route('/auth/firebase_login', methods=['POST'])
    def firebase_login():
        data = request.get_json()
        id_token = data.get('idToken', '')
        
        # Verify token format
        if len(id_token) < 100:
            return jsonify({'error': 'Invalid token format'}), 400
        
        # Mock successful authentication for testing
        return jsonify({
            'success': True,
            'user': {
                'id': 'test-user-123',
                'email': 'test@example.com',
                'name': 'Test User'
            },
            'redirect_url': '/dashboard'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'firebase': 'configured'})
    
    return app

def test_app_endpoints():
    """Test the main app's Firebase endpoints"""
    print("\n" + "=" * 60)
    print("APP ENDPOINTS TEST")
    print("=" * 60)
    
    endpoints = [
        'http://localhost:5000/auth/config',
        'http://localhost:5000/auth/user-status',
        'http://localhost:5000/health'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"✓ {endpoint}: Working")
                if 'json' in response.headers.get('content-type', ''):
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)}")
            else:
                print(f"✗ {endpoint}: Error {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint}: {e}")

def generate_mock_firebase_token():
    """Generate a mock Firebase ID token for testing"""
    import base64
    
    # Create a mock JWT structure
    header = {
        "alg": "RS256",
        "kid": "test-key-id",
        "typ": "JWT"
    }
    
    payload = {
        "iss": f"https://securetoken.google.com/{FIREBASE_CONFIG['projectId']}",
        "aud": FIREBASE_CONFIG['projectId'],
        "auth_time": int(time.time()),
        "user_id": "test-uid-123",
        "sub": "test-uid-123",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "email": "debug-user@smartdispute.ai",
        "email_verified": True,
        "firebase": {
            "identities": {
                "email": ["debug-user@smartdispute.ai"]
            },
            "sign_in_provider": "password"
        }
    }
    
    # Create mock JWT (not cryptographically valid, just for format testing)
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    signature = "mock-signature-for-testing-purposes-only"
    
    mock_token = f"{header_b64}.{payload_b64}.{signature}"
    
    return mock_token

def provide_solutions(token_format):
    """Provide solutions based on the identified issues"""
    print("\n" + "=" * 60)
    print("SOLUTIONS & RECOMMENDATIONS")
    print("=" * 60)
    
    if token_format == "uuid":
        print("ISSUE: UUID provided instead of Firebase ID token")
        print("\nSOLUTIONS:")
        print("1. Use Firebase Authentication to get a proper ID token:")
        print("   - Sign in with Google through Firebase Auth")
        print("   - Call user.getIdToken() to retrieve the authentication token")
        print("   - Use this token for backend verification")
        print("\n2. For testing purposes, here's a mock Firebase token:")
        mock_token = generate_mock_firebase_token()
        print(f"   Mock Token: {mock_token[:100]}...")
        print(f"   Full length: {len(mock_token)} characters")
        
        print("\n3. To get a real Firebase token:")
        print("   - Visit the app at http://localhost:5000")
        print("   - Sign in with Google")
        print("   - Check browser console for the ID token")
        print("   - Use that token for testing")
        
    elif token_format == "unknown":
        print("ISSUE: Unrecognized token format")
        print("\nSOLUTIONS:")
        print("1. Verify you're using a Firebase ID token")
        print("2. Check Firebase authentication flow")
        print("3. Ensure proper token extraction from Firebase Auth")
    
    print("\nNEXT STEPS:")
    print("1. Test the fixed Firebase authentication endpoints")
    print("2. Verify Google OAuth configuration")
    print("3. Test complete authentication flow")

def start_test_server():
    """Start a test server for Firebase debugging"""
    app = create_test_firebase_app()
    
    def run_server():
        app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("\nTest server started on http://localhost:5001")
    print("Endpoints available:")
    print("  GET  /auth/config")
    print("  POST /auth/test-token")
    print("  POST /auth/firebase_login")
    print("  GET  /health")
    
    return server_thread

def main():
    """Main debug function"""
    if len(sys.argv) != 2:
        print("Firebase Debug Tool for SmartDispute.ai")
        print("Usage: python firebase_debug_complete.py <token>")
        print("Example: python firebase_debug_complete.py 06C3F916-79CA-43D9-9FD1-11E1F21FB66B")
        return
    
    token = sys.argv[1]
    
    print("SmartDispute.ai Firebase Complete Debug Tool")
    print(f"Started at: {datetime.now()}")
    
    # Run comprehensive analysis
    token_format = analyze_token_format(token)
    firebase_status = test_firebase_services()
    
    # Start test server
    server_thread = start_test_server()
    time.sleep(2)  # Give server time to start
    
    # Test app endpoints
    test_app_endpoints()
    
    # Provide solutions
    provide_solutions(token_format)
    
    # Final summary
    print("\n" + "=" * 60)
    print("COMPLETE DIAGNOSIS")
    print("=" * 60)
    
    print(f"Token Format: {token_format.upper()}")
    print(f"Firebase Services: {'✓ Available' if all(isinstance(v, int) for v in firebase_status.values()) else '✗ Issues detected'}")
    print(f"Main Issue: {'UUID provided instead of Firebase ID token' if token_format == 'uuid' else 'Token format issue'}")
    
    print("\nRECOMMENDED ACTION:")
    if token_format == "uuid":
        print("Replace the UUID with a proper Firebase ID token obtained through authentication")
    else:
        print("Verify Firebase authentication configuration and token generation")
    
    print(f"\nCompleted at: {datetime.now()}")
    print("Test server will continue running for additional testing...")
    
    # Keep test server running
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down debug tool...")

if __name__ == "__main__":
    main()