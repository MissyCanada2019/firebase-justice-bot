#!/usr/bin/env python3
"""
Justice-Bot - Clean, Production-Ready Canadian Legal Assistant
"""

import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import uuid

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///justice_bot.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cases = db.relationship('Case', backref='user', lazy=True)

# Case Model
class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    legal_issue_type = db.Column(db.String(50))
    merit_score = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! Welcome to Justice-Bot.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_cases = Case.query.filter_by(user_id=current_user.id).order_by(Case.created_at.desc()).limit(5).all()
    stats = {
        'total_cases': Case.query.filter_by(user_id=current_user.id).count(),
        'analyzed_cases': Case.query.filter_by(user_id=current_user.id, status='analyzed').count(),
        'generated_docs': 0,  # Placeholder
        'completion_rate': 0  # Placeholder
    }
    return render_template('main/dashboard.html', user=current_user, stats=stats, cases=user_cases)

@app.route('/new-case', methods=['GET', 'POST'])
@login_required
def new_case():
    if request.method == 'POST':
        case = Case(
            user_id=current_user.id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            legal_issue_type=request.form.get('legal_issue_type'),
            merit_score=75,  # Placeholder - would be calculated by AI
            status='analyzed'
        )
        db.session.add(case)
        db.session.commit()
        
        flash('Case created successfully!', 'success')
        return redirect(url_for('view_case', case_id=case.id))
    
    return render_template('cases/new.html')

@app.route('/case/<case_id>')
@login_required
def view_case(case_id):
    case = Case.query.filter_by(id=case_id, user_id=current_user.id).first_or_404()
    return render_template('cases/view.html', case=case)

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    print("Starting Justice-Bot Canadian Legal Assistant...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)