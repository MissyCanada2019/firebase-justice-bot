"""
Admin routes for Justice-Bot
User management and system administration
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from models import User, Case, Document, db

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied. Administrator privileges required.", 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system statistics"""
    # Get system statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(active=True).count()
    total_cases = Case.query.count()
    analyzed_cases = Case.query.filter(Case.merit_score.isnot(None)).count()
    generated_docs = Case.query.filter_by(document_generated=True).count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_cases = Case.query.order_by(Case.created_at.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_cases': total_cases,
        'analyzed_cases': analyzed_cases,
        'generated_docs': generated_docs,
        'analysis_rate': round((analyzed_cases / total_cases * 100) if total_cases > 0 else 0, 1)
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_users=recent_users,
                         recent_cases=recent_cases)

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all users with management options"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    
    if search:
        query = query.filter(
            User.full_name.contains(search) |
            User.email.contains(search)
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)

@admin_bp.route('/users/<uuid:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot change your own admin status", 'error')
        return redirect(url_for('admin.list_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = "granted" if user.is_admin else "revoked"
    flash(f"Admin privileges {status} for {user.full_name}", 'success')
    
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/<uuid:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    """Toggle active status for a user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot deactivate your own account", 'error')
        return redirect(url_for('admin.list_users'))
    
    user.active = not user.active
    db.session.commit()
    
    status = "activated" if user.active else "deactivated"
    flash(f"Account {status} for {user.full_name}", 'success')
    
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/cases')
@login_required
@admin_required
def list_cases():
    """List all cases with filtering options"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    issue_type_filter = request.args.get('issue_type', '', type=str)
    
    query = Case.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if issue_type_filter:
        query = query.filter_by(legal_issue_type=issue_type_filter)
    
    cases = query.order_by(Case.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get filter options
    statuses = db.session.query(Case.status).distinct().all()
    issue_types = db.session.query(Case.legal_issue_type).distinct().all()
    
    return render_template('admin/cases.html', 
                         cases=cases,
                         statuses=[s[0] for s in statuses if s[0]],
                         issue_types=[t[0] for t in issue_types if t[0]],
                         status_filter=status_filter,
                         issue_type_filter=issue_type_filter)