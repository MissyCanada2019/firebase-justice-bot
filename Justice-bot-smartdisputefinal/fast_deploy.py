#!/usr/bin/env python3
"""
Fast deployment launcher for SmartDispute.ai
This script bootstraps a minimal application first, then loads the full app in the background
"""
import os
import logging
import threading
import time
from flask import Flask, redirect, url_for, render_template_string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a minimal app that responds immediately
app = Flask(__name__)

# Simple HTML template for the loading page
LOADING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartDispute.ai - Loading...</title>
    <meta http-equiv="refresh" content="5"> <!-- Refresh every 5 seconds -->
    
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-05T0V9H01H"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-05T0V9H01H');
    </script>
    
    <!-- Bootstrap Dark Theme CSS -->
    <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #232731;
            color: #e6e6e6;
        }
        .loader {
            border: 16px solid #444;
            border-top: 16px solid #e62e2e;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            animation: spin 2s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .container {
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SmartDispute.ai</h1>
        <div class="loader"></div>
        <p>Loading your legal automation platform...</p>
        <p class="text-muted">This will take less than a minute.</p>
    </div>
</body>
</html>
"""

# Global variable to track if the main app is ready
main_app_ready = False

# Routes for the minimal app
@app.route('/')
def loading_page():
    """Show loading page while the main app is starting"""
    return render_template_string(LOADING_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    if main_app_ready:
        return {"status": "ok", "app": "full"}, 200
    else:
        return {"status": "ok", "app": "minimal"}, 200

def initialize_main_app():
    """Initialize the main application in the background"""
    global main_app_ready
    
    logger.info("Starting main application initialization...")
    time.sleep(2)  # Give the minimal app time to start
    
    try:
        # Import the main app (this will trigger initialization)
        import app as main_app
        logger.info("Main application imported")
        
        # Mark the main app as ready
        main_app_ready = True
        logger.info("Main application is now ready")
        
    except Exception as e:
        logger.error(f"Error initializing main app: {e}")

if __name__ == "__main__":
    # Start the main app initialization in a background thread
    init_thread = threading.Thread(target=initialize_main_app)
    init_thread.daemon = True
    init_thread.start()
    
    # Start the minimal app
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting minimal app on port {port}")
    app.run(host="0.0.0.0", port=port)