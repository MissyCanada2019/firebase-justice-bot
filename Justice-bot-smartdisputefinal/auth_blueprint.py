"""
Simple Authentication for SmartDispute.ai
Fixed implementation of user registration without syntax errors
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import User, db
from flask_login import login_user, current_user
import re
import logging
from urllib.parse import urlparse

auth_bp = Blueprint('auth', __name__)

def is_safe_url(target):
    """
    Check if the target URL is safe for redirect.
    Only allows relative URLs or URLs from the same host.
    """
    if not target:
        return False
    
    # Parse the target URL
    parsed = urlparse(target)
    
    # Allow relative URLs (no netloc)
    if not parsed.netloc:
        return True
    
    # For absolute URLs, only allow same host
    # This would need to be configured for your specific domain
    # For now, we'll be conservative and only allow relative URLs
    return False

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Get current real user count for display
    try:
        real_user_count = User.query.filter_by(is_free_user=True, is_test_user=False).count()
    except Exception as e:
        logging.error(f"Error getting user count: {str(e)}")
        real_user_count = 0
    
    # LOCKDOWN: If we've reached 1000 users, completely disable registration
    if real_user_count >= 1000:
        return render_template('registration_closed.html', user_count=real_user_count)
    
    if request.method == 'POST':
        try:
            # Double-check the limit during registration to prevent race conditions
            current_count = User.query.filter_by(is_free_user=True, is_test_user=False).count()
            if current_count >= 1000:
                flash('The pilot program just reached capacity. Registration is now closed.', 'warning')
                return render_template('registration_closed.html', user_count=current_count)
            
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            province = request.form.get('province', '').strip()
            postal_code = request.form.get('postal_code', '').strip()
            legal_issue_type = request.form.get('legal_issue_type', '').strip()
            password = request.form.get('password', '').strip()
            pilot_consent = request.form.get('pilot_consent') == 'on'
            
            # Basic validation
            if not all([first_name, last_name, email, password]):
                flash('First name, last name, email and password are required.', 'danger')
                return render_template('register.html', user_count=real_user_count)
            
            # Validate email format
            if '@' not in email or '.' not in email:
                flash('Please enter a valid email address.', 'danger')
                return render_template('register.html', user_count=real_user_count)
            
            # Validate postal code if provided
            if postal_code:
                postal_pattern = r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$'
                if not re.match(postal_pattern, postal_code):
                    flash('Please enter a valid Canadian postal code (format: A1A 1A1)', 'danger')
                    return render_template('register.html', user_count=real_user_count)
            
            # Validate phone if provided
            if phone:
                phone_digits = re.sub(r'\D', '', phone)
                if len(phone_digits) < 10:
                    flash('Please enter a valid phone number with at least 10 digits', 'danger')
                    return render_template('register.html', user_count=real_user_count)
                
            if not pilot_consent:
                flash('You must agree to participate in the pilot program to continue', 'danger')
                return render_template('register.html', user_count=real_user_count)
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already exists', 'danger')
                return render_template('register.html', user_count=real_user_count)
                
            # Create new user
            new_user = User()
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.email = email
            new_user.phone = phone or None
            new_user.address = address or None
            new_user.city = city or None
            new_user.province = province or None
            new_user.postal_code = postal_code or None
            new_user.legal_issue_type = legal_issue_type or None
            new_user.is_free_user = True
            new_user.is_test_user = False
            new_user.free_user_number = real_user_count + 1
            new_user.pilot_consent = True
            new_user.email_verified = True
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Auto-login the new user
            login_user(new_user)
            
            flash(f'Welcome to SmartDispute.ai! You are participant #{new_user.free_user_number}/1000 in our free pilot program.', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            return render_template('register.html', user_count=real_user_count)
        
    return render_template('register.html', user_count=real_user_count)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login_simple.html')

@auth_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/pilot-stats')
def pilot_stats():
    """API endpoint for real-time pilot program statistics"""
    try:
        real_users = User.query.filter_by(is_free_user=True, is_test_user=False).count()
        test_users = User.query.filter_by(is_free_user=True, is_test_user=True).count()
        
        return jsonify({
            'real_users': real_users,
            'test_users': test_users,
            'total': real_users + test_users,
            'limit': 1000,
            'slots_remaining': max(0, 1000 - real_users),
            'program_full': real_users >= 1000
        })
    except Exception as e:
        logging.error(f"Error getting pilot stats: {str(e)}")
        return jsonify({'error': 'Unable to get stats'}), 500