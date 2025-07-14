#!/usr/bin/env python3
"""
Fast startup script for SmartDispute.ai
Optimized to bind to port 5000 quickly and initialize components in background
"""

import os
import sys
import threading
import time
from flask import Flask, jsonify, render_template_string

# Create minimal Flask app that binds to port immediately
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'temp-key')

# Flag to track initialization status
initialization_complete = False
main_app = None

@app.route('/')
def index():
    if initialization_complete and main_app:
        # Forward to main application
        return main_app.dispatch_request()
    else:
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>SmartDispute.ai - Loading</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f8f9fa; }
                .loading { color: #b22234; font-size: 24px; margin: 20px 0; }
                .maple { color: #ff0000; font-size: 48px; }
                .progress { width: 300px; height: 20px; background: #e9ecef; border-radius: 10px; margin: 20px auto; overflow: hidden; }
                .progress-bar { height: 100%; background: linear-gradient(45deg, #b22234, #a11d30); border-radius: 10px; animation: loading 3s ease-in-out infinite; }
                @keyframes loading { 0%, 100% { width: 20%; } 50% { width: 80%; } }
            </style>
            <script>
                setTimeout(function() { window.location.reload(); }, 5000);
            </script>
        </head>
        <body>
            <div class="maple">🍁</div>
            <h1>SmartDispute.ai</h1>
            <div class="loading">Initializing Canadian Legal Platform...</div>
            <div class="progress"><div class="progress-bar"></div></div>
            <p>Loading comprehensive legal coverage for all Canadian jurisdictions</p>
            <p><em>"Everyone has the right to life, liberty and security of the person" - Charter Section 7</em></p>
        </body>
        </html>
        ''')

@app.route('/health')
def health():
    return jsonify({
        "status": "ok" if initialization_complete else "initializing",
        "timestamp": time.time(),
        "ready": initialization_complete
    })

@app.route('/pricing')
def pricing():
    if initialization_complete and main_app:
        return main_app.dispatch_request()
    return jsonify({"message": "Pricing page loading...", "status": "initializing"})

def initialize_main_app():
    """Initialize the main application in background"""
    global initialization_complete, main_app
    
    try:
        print("Starting background initialization...")
        
        # Import and initialize main application
        from app import app as main_application
        main_app = main_application
        
        print("Main application initialized successfully")
        initialization_complete = True
        
    except Exception as e:
        print(f"Initialization error: {e}")
        import traceback
        traceback.print_exc()

def start_server():
    """Start the fast server"""
    print("SmartDispute.ai - Fast Start Server")
    print("Binding to port 5000 immediately...")
    
    # Start background initialization
    init_thread = threading.Thread(target=initialize_main_app, daemon=True)
    init_thread.start()
    
    # Start server immediately
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    start_server()