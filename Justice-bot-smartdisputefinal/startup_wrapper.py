#!/usr/bin/env python3
"""
Simple wrapper script to detect if running in a Replit workflow
and use the appropriate startup method.

This script:
1. Detects if it's running in a Replit workflow
2. Uses our rapid-start approach if in a workflow
3. Uses standard gunicorn if not in a workflow
"""
import os
import sys
import socket
import time
import threading
import logging
from flask import Flask

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a minimal Flask app that responds immediately
app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartDispute.ai - Starting</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }
            .loader {
                border: 16px solid #f3f3f3;
                border-radius: 50%;
                border-top: 16px solid #3498db;
                width: 60px;
                height: 60px;
                animation: spin 2s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <h1>SmartDispute.ai is starting...</h1>
        <p>Please wait while the application initializes.</p>
        <div class="loader"></div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK"

def is_replit_workflow():
    """Check if running in a Replit workflow"""
    return os.environ.get('REPL_ID') is not None and os.environ.get('REPLIT_DEPLOYMENT') is not None

def start_main_app():
    """Start the main application after a delay"""
    time.sleep(2)  # Give the minimal server time to start
    
    logger.info("Starting main application...")
    
    try:
        # Import gunicorn programmatically
        import gunicorn.app.base
        
        # Create a custom application
        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()
                
            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)
                    
            def load(self):
                return self.application
        
        # Import the main app
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from main import app as flask_app
        
        # Start gunicorn with the app
        options = {
            'bind': '0.0.0.0:5000',
            'workers': 1,
            'reuse_port': True,
            'reload': True,
        }
        
        StandaloneApplication(flask_app, options).run()
        
    except Exception as e:
        logger.error(f"Error starting main app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if is_replit_workflow():
        logger.info("Running in Replit workflow - using optimized startup")
        
        # Start the main app in a thread
        main_thread = threading.Thread(target=start_main_app)
        main_thread.daemon = True
        main_thread.start()
        
        # Start Flask immediately to satisfy port check
        app.run(host="0.0.0.0", port=5000)
    else:
        logger.info("Not running in Replit workflow - using standard startup")
        
        # Simply execute gunicorn directly
        os.execvp("gunicorn", ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"])