#!/usr/bin/env python3
"""
Simplified main entry point for SmartDispute.ai
Optimized for fast startup to avoid Replit timeout issues
"""
import os
import logging
from flask import Flask, render_template, jsonify

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Create minimal Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Basic configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///temp.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

@app.route('/')
def index():
    """Main landing page"""
    return '''
    <html>
    <head>
        <title>SmartDispute.ai - Canadian Legal Platform</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f8f9fa; }
            .container { max-width: 900px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 40px; }
            .title { color: #dc2626; font-size: 2.5rem; margin: 0; }
            .subtitle { color: #1e40af; font-size: 1.5rem; margin: 10px 0; }
            .quote { font-style: italic; color: #374151; font-size: 1.1rem; margin: 20px 0; }
            .status { background: #ecfdf5; padding: 20px; border-radius: 8px; border-left: 4px solid #059669; margin: 20px 0; }
            .pilot { background: #fef3c7; padding: 20px; border-radius: 8px; border-left: 4px solid #d97706; margin: 20px 0; }
            .nav { text-align: center; margin: 30px 0; }
            .nav a { color: #1e40af; text-decoration: none; margin: 0 15px; font-weight: 500; }
            .nav a:hover { text-decoration: underline; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
            .feature { background: #f9fafb; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; }
            .feature h3 { color: #1f2937; margin: 0 0 10px; }
            .maple { color: #dc2626; font-size: 1.2em; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title"><span class="maple">🍁</span> SmartDispute.ai</h1>
                <h2 class="subtitle">Canadian Legal Empowerment Platform</h2>
                <p class="quote">
                    "Everyone has the right to life, liberty and security of the person"<br>
                    - Canadian Charter of Rights and Freedoms, Section 7
                </p>
            </div>

            <div class="status">
                <h3 style="color: #059669; margin: 0 0 10px;">✓ Application Running Successfully</h3>
                <p style="margin: 0;">SmartDispute.ai is now accessible and ready to help Canadians navigate legal challenges.</p>
            </div>

            <div class="pilot">
                <h3 style="color: #d97706; margin: 0 0 10px;">Pilot Program Active</h3>
                <p style="margin: 0;">Free access for the first 1000 Canadian users. Join our mission to democratize legal justice and make courts places of real fairness.</p>
            </div>

            <div class="features">
                <div class="feature">
                    <h3>AI Legal Analysis</h3>
                    <p>Upload documents and get comprehensive analysis of your legal situation with merit scoring.</p>
                </div>
                <div class="feature">
                    <h3>Court Document Generation</h3>
                    <p>Generate properly formatted legal documents ready for Canadian court filing.</p>
                </div>
                <div class="feature">
                    <h3>Charter Rights Protection</h3>
                    <p>Ensure your constitutional rights are protected throughout legal proceedings.</p>
                </div>
                <div class="feature">
                    <h3>Case Management</h3>
                    <p>Track your legal case progress with timeline milestones and next action recommendations.</p>
                </div>
            </div>

            <div class="nav">
                <a href="/health">Health Check</a>
                <a href="/register">Join Pilot</a>
                <a href="/login">Sign In</a>
                <a href="/about">About</a>
                <a href="/pricing">Pricing</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SmartDispute.ai",
        "version": "1.0.0",
        "message": "Canadian Legal Platform running successfully"
    })

@app.route('/register')
def register():
    """Registration page placeholder"""
    return '''
    <html>
    <head><title>Join SmartDispute.ai Pilot</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
            <h1 style="color: #dc2626;">🍁 Join SmartDispute.ai Pilot</h1>
            <p>Registration system is currently being set up. Please check back soon!</p>
            <p><a href="/" style="color: #1e40af;">← Back to Home</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/login')
def login():
    """Login page placeholder"""
    return '''
    <html>
    <head><title>Sign In - SmartDispute.ai</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
            <h1 style="color: #dc2626;">🍁 Sign In to SmartDispute.ai</h1>
            <p>Authentication system is currently being configured. Please check back soon!</p>
            <p><a href="/" style="color: #1e40af;">← Back to Home</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/about')
def about():
    """About page"""
    return '''
    <html>
    <head><title>About SmartDispute.ai</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa;">
        <div style="max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
            <h1 style="color: #dc2626;">🍁 About SmartDispute.ai</h1>
            <h2 style="color: #1e40af;">Our Mission</h2>
            <p>SmartDispute.ai is dedicated to making courtrooms "a place of real fairness and justice, not a game of money and privilege." We provide AI-powered legal assistance to help Canadians navigate complex legal processes.</p>
            
            <h2 style="color: #1e40af;">Canadian Focus</h2>
            <p>Our platform is specifically designed for Canadian law, incorporating federal, provincial, and municipal legal frameworks, with special emphasis on Charter rights protection.</p>
            
            <h2 style="color: #1e40af;">Pilot Program</h2>
            <p>We're currently offering free access to the first 1000 Canadian users to test and improve our platform before the official launch.</p>
            
            <p><a href="/" style="color: #1e40af;">← Back to Home</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/pricing')
def pricing():
    """Pricing page"""
    return '''
    <html>
    <head><title>Pricing - SmartDispute.ai</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa;">
        <div style="max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
            <h1 style="color: #dc2626;">🍁 SmartDispute.ai Pricing</h1>
            
            <div style="background: #ecfdf5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669;">
                <h2 style="color: #059669; margin: 0 0 10px;">Pilot Program - FREE</h2>
                <p style="margin: 0;">First 1000 Canadian users get full access at no cost during our testing phase.</p>
            </div>
            
            <h2 style="color: #1e40af;">Future Pricing (Post-Pilot)</h2>
            <ul>
                <li><strong>Basic Plan:</strong> $29.99/month - Core legal assistance</li>
                <li><strong>Premium Plan:</strong> $59.99/month - Advanced case management</li>
                <li><strong>Low-Income:</strong> $15.99/year - Verified assistance recipients</li>
            </ul>
            
            <p><a href="/" style="color: #1e40af;">← Back to Home</a></p>
        </div>
    </body>
    </html>
    '''

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return '''
    <html>
    <head><title>Page Not Found - SmartDispute.ai</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
            <h1 style="color: #dc2626;">🍁 Page Not Found</h1>
            <p>The requested page does not exist.</p>
            <p><a href="/" style="color: #1e40af;">← Back to Home</a></p>
        </div>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return '''
    <html>
    <head><title>Server Error - SmartDispute.ai</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px;">
            <h1 style="color: #dc2626;">🍁 Server Error</h1>
            <p>An internal server error occurred. Please try again later.</p>
            <p><a href="/" style="color: #1e40af;">← Back to Home</a></p>
        </div>
    </body>
    </html>
    ''', 500

if __name__ == '__main__':
    print("Starting SmartDispute.ai simplified server...")
    app.run(host='0.0.0.0', port=5000, debug=True)