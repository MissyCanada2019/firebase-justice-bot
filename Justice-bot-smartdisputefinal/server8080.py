"""
Direct server on port 8080 for SmartDispute.ai
Simplified version that runs the app directly on port 8080
"""
import os
from app import app

if __name__ == "__main__":
    port = 8080
    print(f"Starting SmartDispute.ai on port {port}")
    app.run(host="0.0.0.0", port=port)