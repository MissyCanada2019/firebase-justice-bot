"""
Admin System for SmartDispute.ai
Handles test account creation, user management, and admin authentication
"""
import os
import secrets
import string
from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from models import User
import logging
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def is_admin(user):
    """Check if user has admin privileges"""
    return user and hasattr(user, 'is_admin') and user.is_admin

def require_admin(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not is_admin(current_user):
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@login_required
@require_admin
def dashboard():
    """Admin dashboard"""
    total_users = User.query.count()
    test_users = User.query.filter_by(role='test_user').count()
    admin_users = User.query.filter(User.role.in_(['admin', 'superadmin'])).count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         test_users=test_users,
                         admin_users=admin_users,
                         recent_users=recent_users)

@admin_bp.route('/create-test-accounts', methods=['GET', 'POST'])
@login_required
@require_admin
def create_test_accounts():
    """Create test accounts for users"""
    if request.method == 'POST':
        try:
            num_accounts = int(request.form.get('num_accounts', 5))
            account_type = request.form.get('account_type', 'test_user')
            
            if num_accounts > 50:
                flash('Maximum 50 accounts can be created at once', 'error')
                return redirect(url_for('admin.create_test_accounts'))
            
            created_accounts = []
            
            for i in range(num_accounts):
                # Generate unique test account
                username = f"test_user_{secrets.token_hex(4)}"
                email = f"{username}@testuser.smartdispute.ai"
                password = generate_secure_password()
                
                # Check if email already exists
                if User.query.filter_by(email=email).first():
                    continue
                
                # Create test user
                test_user = User(
                    id=str(uuid.uuid4()),
                    username=username,
                    email=email,
                    first_name=f"Test",
                    last_name=f"User {i+1}",
                    role=account_type,
                    email_verified=True,
                    account_status='active',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                test_user.set_password(password)
                
                db.session.add(test_user)
                
                created_accounts.append({
                    'username': username,
                    'email': email,
                    'password': password,
                    'role': account_type
                })
            
            db.session.commit()
            
            logger.info(f"Admin {current_user.email} created {len(created_accounts)} test accounts")
            
            return render_template('admin/test_accounts_created.html',
                                 accounts=created_accounts)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating test accounts: {e}")
            flash('Error creating test accounts', 'error')
    
    return render_template('admin/create_test_accounts.html')

@admin_bp.route('/user-management')
@login_required
@require_admin
def user_management():
    """User management interface"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.email.contains(search)) |
            (User.username.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/user_management.html',
                         users=users,
                         search=search,
                         role_filter=role_filter)

@admin_bp.route('/update-user/<user_id>', methods=['POST'])
@login_required
@require_admin
def update_user(user_id):
    """Update user details"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent modifying superadmin unless current user is superadmin
        if user.role == 'superadmin' and current_user.role != 'superadmin':
            flash('Cannot modify superadmin accounts', 'error')
            return redirect(url_for('admin.user_management'))
        
        user.role = request.form.get('role', user.role)
        user.account_status = request.form.get('account_status', user.account_status)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Admin {current_user.email} updated user {user.email}")
        flash(f'User {user.email} updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user: {e}")
        flash('Error updating user', 'error')
    
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/create-admin', methods=['GET', 'POST'])
@login_required
@require_admin
def create_admin():
    """Create admin account (superadmin only)"""
    if current_user.role != 'superadmin':
        flash('Superadmin access required', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            username = request.form.get('username')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            role = request.form.get('role', 'admin')
            password = generate_secure_password(16)
            
            # Check if user exists
            if User.query.filter_by(email=email).first():
                flash('User with this email already exists', 'error')
                return render_template('admin/create_admin.html')
            
            # Create admin user
            admin_user = User(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                email_verified=True,
                account_status='active',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            admin_user.set_password(password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            logger.info(f"Superadmin {current_user.email} created admin account {email}")
            
            return render_template('admin/admin_created.html',
                                 email=email,
                                 password=password,
                                 role=role)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating admin: {e}")
            flash('Error creating admin account', 'error')
    
    return render_template('admin/create_admin.html')

@admin_bp.route('/test-accounts-list')
@login_required
@require_admin
def test_accounts_list():
    """List all test accounts"""
    test_accounts = User.query.filter_by(role='test_user').order_by(User.created_at.desc()).all()
    
    return render_template('admin/test_accounts_list.html',
                         test_accounts=test_accounts)

@admin_bp.route('/reset-user-password/<user_id>', methods=['POST'])
@login_required
@require_admin
def reset_user_password(user_id):
    """Reset user password"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent resetting superadmin password unless current user is superadmin
        if user.role == 'superadmin' and current_user.role != 'superadmin':
            flash('Cannot reset superadmin password', 'error')
            return redirect(url_for('admin.user_management'))
        
        new_password = generate_secure_password(12)
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Admin {current_user.email} reset password for user {user.email}")
        
        return jsonify({
            'success': True,
            'email': user.email,
            'new_password': new_password
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting password: {e}")
        return jsonify({'success': False, 'error': 'Failed to reset password'})

def create_initial_admin():
    """Create initial admin account if none exists"""
    try:
        # Check if any admin exists
        admin_exists = User.query.filter_by(is_admin=True).first()
        
        if not admin_exists:
            # Create initial superadmin
            admin_email = "admin@smartdispute.ai"
            admin_password = generate_secure_password(16)
            
            admin_user = User(
                email=admin_email,
                first_name="System",
                last_name="Administrator",
                is_admin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            admin_user.set_password(admin_password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            logger.info(f"Initial admin account created: {admin_email}")
            logger.info(f"Initial admin password: {admin_password}")
            
            # Also create a file with admin credentials
            with open('ADMIN_CREDENTIALS.txt', 'w') as f:
                f.write(f"SmartDispute.ai Initial Admin Account\n")
                f.write(f"=====================================\n")
                f.write(f"Email: {admin_email}\n")
                f.write(f"Password: {admin_password}\n")
                f.write(f"Role: superadmin\n")
                f.write(f"Created: {datetime.utcnow()}\n")
                f.write(f"\nIMPORTANT: Change this password immediately after first login!\n")
            
            return admin_email, admin_password
            
    except Exception as e:
        logger.error(f"Error creating initial admin: {e}")
        db.session.rollback()
        
    return None, None

def init_admin_system(app):
    """Initialize admin system with the Flask app"""
    app.register_blueprint(admin_bp)
    
    # Create initial admin if needed
    with app.app_context():
        admin_email, admin_password = create_initial_admin()
        if admin_email:
            logger.info("Admin system initialized with initial admin account")
    
    logger.info("Admin system initialized")