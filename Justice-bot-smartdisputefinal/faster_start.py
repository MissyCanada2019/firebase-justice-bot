#!/usr/bin/env python3
"""
Fast-startup version of the SmartDispute.ai application
This starts with minimal resources to ensure faster detection by the Replit workflow system
"""
import os
import socket
import sys
import threading
import time

# Create a simple app that responds immediately
from flask import Flask

app = Flask(__name__)

@app.route('/')
def loading():
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
                color: #333;
            }
            h1 {
                color: #0056b3;
            }
            .loading {
                display: inline-block;
                position: relative;
                width: 80px;
                height: 80px;
            }
            .loading div {
                position: absolute;
                border: 4px solid #0056b3;
                opacity: 1;
                border-radius: 50%;
                animation: loading 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
            }
            .loading div:nth-child(2) {
                animation-delay: -0.5s;
            }
            @keyframes loading {
                0% {
                    top: 36px;
                    left: 36px;
                    width: 0;
                    height: 0;
                    opacity: 1;
                }
                100% {
                    top: 0px;
                    left: 0px;
                    width: 72px;
                    height: 72px;
                    opacity: 0;
                }
            }
        </style>
    </head>
    <body>
        <h1>SmartDispute.ai is starting...</h1>
        <p>Please wait while the application initializes.</p>
        <div class="loading"><div></div><div></div></div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK"

def check_port_available(port):
    """Check if a port is available for binding"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', port))
        s.close()
        return True
    except:
        return False

def start_main_app():
    """Start the main application in a subprocess"""
    time.sleep(3)  # Wait for Flask to start
    print("Starting main application...")
    
    try:
        # Start gunicorn with main:app
        main_cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
        
        # Replace current process with gunicorn
        os.execvp(main_cmd[0], main_cmd)
    except Exception as e:
        print(f"Error starting main app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting minimal Flask application for fast detection...")
    
    # Start the main app in a thread
    main_thread = threading.Thread(target=start_main_app)
    main_thread.daemon = True
    main_thread.start()
    
    # Start Flask on port 5000
    print("Starting Flask on port 5000")
    app.run(host='0.0.0.0', port=5000)