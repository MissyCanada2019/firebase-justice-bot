"""
Simplified User Model for SmartDispute.ai Pilot Program
Clean implementation focusing on essential fields for 1000 user tracking
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = "users_pilot"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Basic profile information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Address information
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    
    # Legal case information
    legal_issue_type = db.Column(db.String(50), nullable=False)
    
    # Pilot program tracking
    is_admin = db.Column(db.Boolean, default=False)
    is_test_user = db.Column(db.Boolean, default=False)  # Flag for test users
    is_free_user = db.Column(db.Boolean, default=True)   # For the first 1000 users
    free_user_number = db.Column(db.Integer, nullable=True)  # User's position in free program
    pilot_consent = db.Column(db.Boolean, default=False)  # Consent for pilot program data usage
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_display_location(self):
        return f"{self.city}, {self.province}"
    
    def __repr__(self):
        return f'<User {self.email} #{self.free_user_number if self.free_user_number else "N/A"}>'


# Simple case tracking for pilot program
class PilotCase(db.Model):
    __tablename__ = "pilot_cases"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_pilot.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    legal_issue_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship back to user
    user = db.relationship('User', backref=db.backref('pilot_cases', lazy=True))
    
    def __repr__(self):
        return f'<PilotCase {self.title} - {self.status}>'


# Simple document tracking for pilot program
class PilotDocument(db.Model):
    __tablename__ = "pilot_documents"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_pilot.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('pilot_cases.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('pilot_documents', lazy=True))
    case = db.relationship('PilotCase', backref=db.backref('documents', lazy=True))
    
    def __repr__(self):
        return f'<PilotDocument {self.filename}>'