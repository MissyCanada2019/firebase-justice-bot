"""
Authentication routes for Justice-Bot
Canadian legal platform registration and login
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with Canadian legal branding"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        province = request.form.get('province', '')
        postal_code = request.form.get('postal_code', '').strip().upper()
        
        # Validation
        errors = []
        
        if not full_name or len(full_name) < 2:
            errors.append("Please enter your full name")
        
        if not email or '@' not in email:
            errors.append("Please enter a valid email address")
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if not province:
            errors.append("Please select your province or territory")
        
        if not postal_code or len(postal_code) < 6:
            errors.append("Please enter a valid Canadian postal code")
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            user = User()
            user.full_name = full_name
            user.email = email
            user.province = province
            user.postal_code = postal_code
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Auto-login after registration
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash("Welcome to Justice-Bot! Your account has been created successfully.", 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating your account. Please try again.", 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with Canadian legal branding"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        if not email or not password:
            flash("Please enter both email and password", 'error')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if hasattr(user, 'active') and not user.active:
                flash("Your account has been suspended. Please contact support.", 'error')
                return render_template('auth/login.html')
            
            # Successful login
            login_user(user, remember=remember_me)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            flash(f"Welcome back, {user.full_name}!", 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash("Email address not found in our system or incorrect password", 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    full_name = current_user.full_name
    logout_user()
    flash(f"You have been signed out successfully. Thank you for using Justice-Bot, {full_name}!", 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)