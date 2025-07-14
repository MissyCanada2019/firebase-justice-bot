"""
Google OAuth Authentication for SmartDispute.ai
Uses the new Google OAuth credentials provided by the user
"""
import os
import json
import requests
import uuid
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
from app import db
from models import User
import logging

logger = logging.getLogger(__name__)

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth 2.0 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

google_oauth_bp = Blueprint('google_oauth', __name__, url_prefix='/auth')

def get_google_provider_cfg():
    """Get Google's OpenID Connect configuration"""
    try:
        return requests.get(GOOGLE_DISCOVERY_URL).json()
    except Exception as e:
        logger.error(f"Failed to get Google provider config: {e}")
        return None

@google_oauth_bp.route("/google")
def google_login():
    """Initiate Google OAuth login"""
    try:
        # Get Google's provider configuration
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            return jsonify({"error": "Failed to get Google configuration"}), 500
        
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Use Replit domain for redirect
        replit_domain = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        redirect_uri = f"https://{replit_domain}/auth/google/callback"
        
        # Create authorization URL
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
        )
        
        return redirect(request_uri)
        
    except Exception as e:
        logger.error(f"Google login error: {e}")
        return jsonify({"error": "Authentication failed"}), 500

@google_oauth_bp.route("/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code from query string
        code = request.args.get("code")
        if not code:
            return jsonify({"error": "No authorization code received"}), 400
        
        # Get Google's provider configuration
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            return jsonify({"error": "Failed to get Google configuration"}), 500
        
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Use Replit domain for redirect
        replit_domain = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        redirect_uri = f"https://{replit_domain}/auth/google/callback"
        
        # Prepare token request
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=redirect_uri,
            code=code
        )
        
        # Exchange code for token
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        # Parse the tokens
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        if userinfo_response.status_code != 200:
            return jsonify({"error": "Failed to get user info from Google"}), 500
        
        # Parse user info
        userinfo = userinfo_response.json()
        
        # Verify email is available and verified
        if not userinfo.get("email_verified"):
            return jsonify({"error": "Email not verified by Google"}), 400
        
        # Create or get user
        user = create_or_update_google_user(userinfo)
        if not user:
            return jsonify({"error": "Failed to create user account"}), 500
        
        # Log user in
        login_user(user, remember=True)
        
        # Store Google user info in session
        session['google_user'] = {
            'email': userinfo['email'],
            'name': userinfo.get('name'),
            'picture': userinfo.get('picture')
        }
        
        logger.info(f"User {user.email} logged in via Google OAuth")
        
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        return jsonify({"error": "Authentication failed"}), 500

def create_or_update_google_user(userinfo):
    """Create or update user from Google OAuth data"""
    try:
        email = userinfo['email']
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User()
            user.email = email
            user.first_name = userinfo.get('given_name', '')
            user.last_name = userinfo.get('family_name', '')
            user.profile_image_url = userinfo.get('picture')
            user.email_verified = userinfo.get('email_verified', False)
            user.created_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            db.session.add(user)
        else:
            # Update existing user
            user.first_name = userinfo.get('given_name', user.first_name)
            user.last_name = userinfo.get('family_name', user.last_name)
            user.profile_image_url = userinfo.get('picture', user.profile_image_url)
            user.email_verified = userinfo.get('email_verified', user.email_verified)
            user.auth_provider = 'google'
            user.google_id = userinfo.get('sub')
            user.updated_at = datetime.utcnow()
        
        db.session.commit()
        return user
        
    except Exception as e:
        logger.error(f"Error creating/updating Google user: {e}")
        db.session.rollback()
        return None

@google_oauth_bp.route("/logout")
def google_logout():
    """Handle Google OAuth logout"""
    try:
        # Clear Flask-Login session
        logout_user()
        
        # Clear Google session data
        session.pop('google_user', None)
        
        # Clear all session data
        session.clear()
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Google logout error: {e}")
        return redirect(url_for('index'))

def init_google_oauth(app):
    """Initialize Google OAuth with the Flask app"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        logger.warning("Google OAuth credentials not found - Google authentication will be disabled")
        return False
    
    app.register_blueprint(google_oauth_bp)
    logger.info("Google OAuth authentication initialized")
    return True