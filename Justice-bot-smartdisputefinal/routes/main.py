"""
Main routes for Justice-Bot
Landing page, dashboard, conversational assistant, and core navigation
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import User, Case, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page for Justice-Bot"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing cases and account info"""
    # Get user's cases
    cases = current_user.cases.order_by(Case.created_at.desc()).limit(10).all()
    
    # Calculate statistics
    total_cases = current_user.cases.count()
    analyzed_cases = current_user.cases.filter(Case.merit_score.isnot(None)).count()
    generated_docs = current_user.cases.filter(Case.document_generated == True).count()
    
    stats = {
        'total_cases': total_cases,
        'analyzed_cases': analyzed_cases,
        'generated_docs': generated_docs,
        'completion_rate': round((analyzed_cases / total_cases * 100) if total_cases > 0 else 0, 1)
    }
    
    return render_template('main/dashboard.html', 
                         cases=cases, 
                         stats=stats,
                         user=current_user)

@main_bp.route('/about')
def about():
    """About Justice-Bot page"""
    return render_template('main/about.html')

@main_bp.route('/help')
def help():
    """Help and FAQ page"""
    return render_template('main/help.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html')

@main_bp.route('/assistant')
def assistant():
    """Conversational AI assistant for legal triage"""
    return render_template('assistant.html')

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Justice-Bot",
        "version": "1.0.0",
        "message": "Canadian Legal Platform running successfully"
    }
