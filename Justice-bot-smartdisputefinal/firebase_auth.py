"""
Firebase Authentication Integration for SmartDispute.ai
Provides secure Google authentication with Canadian Charter compliance
"""
import os
import logging
import requests
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, url_for, session, flash, jsonify
from flask_login import login_user, logout_user, current_user
from app import db
from models import User
import uuid

firebase_bp = Blueprint('firebase_auth', __name__, url_prefix='/auth')
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

def verify_firebase_token(id_token):
    """Verify Firebase ID token and return user data"""
    try:
        # Verify token with Firebase
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_CONFIG['apiKey']}"
        
        payload = {
            "idToken": id_token
        }
        
        response = requests.post(verify_url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if 'users' in data and len(data['users']) > 0:
                user_data = data['users'][0]
                return {
                    'uid': user_data.get('localId'),
                    'email': user_data.get('email'),
                    'name': user_data.get('displayName'),
                    'photo_url': user_data.get('photoUrl'),
                    'email_verified': user_data.get('emailVerified', False)
                }
        
        logger.error(f"Firebase token verification failed: {response.text}")
        return None
        
    except Exception as e:
        logger.error(f"Error verifying Firebase token: {e}")
        return None

def create_or_update_user(firebase_user_data):
    """Create or update user from Firebase data"""
    try:
        # Check if user exists
        user = User.query.filter_by(email=firebase_user_data['email']).first()
        
        if not user:
            # Create new user
            user = User()
            user.email = firebase_user_data['email']
            user.firebase_uid = firebase_user_data['uid']
            user.first_name = firebase_user_data.get('name', '').split(' ')[0] if firebase_user_data.get('name') else ''
            user.last_name = ' '.join(firebase_user_data.get('name', '').split(' ')[1:]) if firebase_user_data.get('name') and len(firebase_user_data.get('name', '').split(' ')) > 1 else ''
            user.profile_image_url = firebase_user_data.get('photo_url')
            user.email_verified = firebase_user_data.get('email_verified', False)
            user.created_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            db.session.add(user)
        else:
            # Update existing user
            user.firebase_uid = firebase_user_data['uid']
            user.profile_image_url = firebase_user_data.get('photo_url')
            user.email_verified = firebase_user_data.get('email_verified', False)
            user.updated_at = datetime.utcnow()
        
        db.session.commit()
        return user
        
    except Exception as e:
        logger.error(f"Error creating/updating user: {e}")
        db.session.rollback()
        return None

@firebase_bp.route('/firebase_login', methods=['POST'])
def firebase_login():
    """Handle Firebase authentication callback"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        
        if not id_token:
            return jsonify({'error': 'No ID token provided'}), 400
        
        # Verify the Firebase token
        firebase_user_data = verify_firebase_token(id_token)
        
        if not firebase_user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Create or update user in database
        user = create_or_update_user(firebase_user_data)
        
        if not user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Log the user in
        login_user(user, remember=True)
        
        # Store Firebase data in session
        session['firebase_user'] = {
            'uid': firebase_user_data['uid'],
            'email': firebase_user_data['email'],
            'name': firebase_user_data.get('name'),
            'photo_url': firebase_user_data.get('photo_url')
        }
        
        logger.info(f"User {user.email} logged in via Firebase")
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'photo_url': user.profile_image_url
            },
            'redirect_url': url_for('main.dashboard')
        })
        
    except Exception as e:
        logger.error(f"Firebase login error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@firebase_bp.route('/firebase-logout', methods=['POST'])
def firebase_logout():
    """Handle Firebase logout"""
    try:
        # Clear Flask-Login session
        logout_user()
        
        # Clear Firebase session data
        session.pop('firebase_user', None)
        
        # Clear all session data
        session.clear()
        
        return jsonify({'success': True, 'redirect_url': url_for('main.index')})
        
    except Exception as e:
        logger.error(f"Firebase logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@firebase_bp.route('/config')
def firebase_config():
    """Provide Firebase configuration for client-side"""
    return jsonify(FIREBASE_CONFIG)

@firebase_bp.route('/user-status')
def user_status():
    """Check current user authentication status"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': f"{current_user.first_name} {current_user.last_name}".strip(),
                'photo_url': current_user.profile_image_url
            }
        })
    else:
        return jsonify({'authenticated': False})

def init_firebase_auth(app):
    """Initialize Firebase authentication with the Flask app"""
    app.register_blueprint(firebase_bp)
    logger.info("Firebase authentication initialized")