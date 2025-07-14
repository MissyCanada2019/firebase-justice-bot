#!/usr/bin/env python3
"""
Optimized entry point for SmartDispute.ai application
This version minimizes startup time by deferring some initialization until after port binding
"""
import os
import threading
import time
from flask import Flask, redirect, url_for, render_template_string

# Create a minimal Flask app that responds immediately
app = Flask(__name__)

@app.route('/health')
def health_check():
    return "OK"

@app.route('/')
def index():
    """Temporary index that redirects to the main app when it's ready"""
    # Check if app initialization is complete
    if hasattr(app, 'initialized') and app.initialized:
        return redirect(url_for('index', _external=True))
    
    # Show loading page
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartDispute.ai - Starting</title>
        <meta http-equiv="refresh" content="5"> <!-- Refresh every 5 seconds -->
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #0056b3;
                text-align: center;
            }
            .loader {
                border: 16px solid #f3f3f3;
                border-top: 16px solid #0056b3;
                border-radius: 50%;
                width: 80px;
                height: 80px;
                animation: spin 1.5s linear infinite;
                margin: 30px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .info {
                text-align: center;
                color: #666;
                font-size: 14px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SmartDispute.ai</h1>
            <p style="text-align: center;">The application is starting up. Please wait a moment...</p>
            <div class="loader"></div>
            <p class="info">This page will automatically refresh when the application is ready.</p>
        </div>
    </body>
    </html>
    """)

def initialize_app_background():
    """Initialize the app in the background after port binding"""
    time.sleep(2)  # Give Flask time to start
    
    print("Initializing application...")
    
    try:
        # Import the real app
        from app import app as real_app
        
        # Copy all the real app's attributes to this app
        for attr in dir(real_app):
            if not attr.startswith('__'):
                setattr(app, attr, getattr(real_app, attr))
        
        # Mark as initialized
        app.initialized = True
        
        print("Application initialization complete")
        
    except Exception as e:
        print(f"Error initializing app: {e}")

if __name__ == "__main__":
    # Start initialization in the background
    init_thread = threading.Thread(target=initialize_app_background)
    init_thread.daemon = True
    init_thread.start()
    
    # Start Flask immediately to respond to port checks
    app.run(host="0.0.0.0", port=5000)