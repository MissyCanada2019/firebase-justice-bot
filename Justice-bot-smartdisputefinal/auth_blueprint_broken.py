"""
Authentication Blueprint for SmartDispute.ai
Clean implementation of user registration with 1000 user limit tracking
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import User, db
from flask_login import login_user, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Get current real user count for display (excluding test users from the limit)
    try:
        real_user_count = User.query.filter_by(is_free_user=True, is_test_user=False).count()
    except Exception as e:
        import logging
        logging.error(f"Error getting user count: {str(e)}")
        real_user_count = 0
    
    if request.method == 'POST':
        try:
            # Check if we've reached the 1000 real user limit
            if real_user_count >= 1000:
                flash('The free pilot program is now full. We have reached our limit of 1000 participants. Thank you for your interest!', 'warning')
                return render_template('register.html', user_count=real_user_count, program_full=True)
            
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            city = request.form.get('city')
            province = request.form.get('province')
            postal_code = request.form.get('postal_code')
            legal_issue_type = request.form.get('legal_issue_type')
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm', password)  # Use password if no confirm field
            pilot_consent = request.form.get('pilot_consent') == 'on'
            
            # Enhanced validation for legal document generation
            if not all([first_name, last_name, email, phone, address, city, province, postal_code, legal_issue_type, password]):
                flash('All fields are required for legal document generation. Please complete your full legal information.', 'danger')
                return render_template('register.html', user_count=real_user_count)
            
            # Validate Canadian postal code format
            import re
            if postal_code and not re.match(r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$', postal_code):
                flash('Please enter a valid Canadian postal code (format: A1A 1A1)', 'danger')
                return render_template('register.html', user_count=real_user_count)
            
            # Validate phone number has at least 10 digits
            if phone:
                phone_digits = re.sub(r'\D', '', phone)
                if len(phone_digits) < 10:
                    flash('Please enter a valid phone number with at least 10 digits', 'danger')
                    return render_template('register.html', user_count=real_user_count)
            
            if password != password_confirm:
                flash('Passwords do not match', 'danger')
                return render_template('register.html', user_count=real_user_count)
                
            if not pilot_consent:
                flash('You must agree to participate in the pilot program to continue', 'danger')
                return render_template('register.html', user_count=real_user_count)
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already exists', 'danger')
                return render_template('register.html', user_count=real_user_count)
                
            # Create new comprehensive user profile
            new_user = User()
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.email = email
            new_user.phone = phone
            new_user.address = address
            new_user.city = city
            new_user.province = province
            new_user.postal_code = postal_code
            new_user.legal_issue_type = legal_issue_type
            new_user.is_free_user = True
            new_user.is_test_user = False  # Real users are not test users
            new_user.free_user_number = real_user_count + 1
            new_user.pilot_consent = True
            new_user.email_verified = True
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Auto-login the new user
            login_user(new_user)
            
            flash(f'Welcome to SmartDispute.ai! You are participant #{new_user.free_user_number}/1000 in our free pilot program. Your account is ready for legal case management.', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            import logging
            logging.error(f"Registration error: {str(e)}")
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            return render_template('register.html', user_count=real_user_count)
        
    return render_template('register.html', user_count=real_user_count)


@auth_bp.route('/pilot-stats')
def pilot_stats():
    """API endpoint for real-time pilot program statistics"""
    real_users = User.query.filter_by(is_free_user=True, is_test_user=False).count()
    test_users = User.query.filter_by(is_free_user=True, is_test_user=True).count()
    
    return {
        'real_users': real_users,
        'test_users': test_users,
        'total': real_users + test_users,
        'limit': 1000,
        'slots_remaining': max(0, 1000 - real_users),
        'program_full': real_users >= 1000
    }

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))