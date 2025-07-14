#!/usr/bin/env python3
"""
Direct Port 8080 Application for SmartDispute.ai

This script creates a direct Flask application on port 8080
"""

from flask import Flask, redirect

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Redirect all traffic to the main application URL"""
    target = f"http://localhost:5000/{path}"
    return redirect(target)

if __name__ == "__main__":
    print("Starting port 8080 application...")
    app.run(host='0.0.0.0', port=8080, debug=False)
