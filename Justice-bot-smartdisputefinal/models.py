"""
Database models for SmartDispute.ai
Includes User, Case, and Document models with proper relationships
"""

from datetime import datetime
from database_fix import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import String, Text, Boolean, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    """User model with authentication and profile information"""
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(String(255), nullable=False)
    
    # Profile information
    full_name = db.Column(String(100), nullable=False)
    phone = db.Column(String(20))
    postal_code = db.Column(String(10))
    province = db.Column(String(50))
    city = db.Column(String(100))
    
    # Account settings
    is_admin = db.Column(Boolean, default=False)
    active = db.Column(Boolean, default=True)  # Renamed to avoid UserMixin conflict
    email_verified = db.Column(Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(DateTime)
    
    # Relationships
    cases = relationship('Case', back_populates='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Case(db.Model):
    """Case model for legal matters with AI analysis"""
    __tablename__ = 'cases'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Case basic information
    title = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    legal_issue_type = db.Column(String(100))  # Family, Criminal, Civil, etc.
    
    # AI Analysis results
    merit_score = db.Column(Integer)  # 1-100 score
    classification = db.Column(String(100))  # AI-determined classification
    ai_summary = db.Column(Text)  # AI-generated case summary
    recommended_actions = db.Column(Text)  # JSON string of recommendations
    
    # Case status
    status = db.Column(String(50), default='draft')  # draft, analyzed, document_generated, filed
    document_generated = db.Column(Boolean, default=False)
    document_path = db.Column(String(500))  # Path to generated document
    
    # Court information
    court_type = db.Column(String(100))  # Based on classification
    court_location = db.Column(Text)  # JSON with court details
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = db.Column(DateTime)
    
    # Relationships
    user = relationship('User', back_populates='cases')
    documents = relationship('Document', back_populates='case', lazy='dynamic')
    
    def __repr__(self):
        return f'<Case {self.title}>'

class Document(db.Model):
    """Document model for uploaded evidence and generated files"""
    __tablename__ = 'documents'
    
    id = db.Column(Integer, primary_key=True)
    case_id = db.Column(Integer, ForeignKey('cases.id'), nullable=False)
    
    # Document information
    filename = db.Column(String(255), nullable=False)
    original_filename = db.Column(String(255), nullable=False)
    file_path = db.Column(String(500), nullable=False)
    file_size = db.Column(Integer)  # Size in bytes
    content_type = db.Column(String(100))
    
    # Document classification
    document_type = db.Column(String(50))  # evidence, generated_document, form
    evidence_type = db.Column(String(50))  # supporting, opposition, neutral
    
    # Content analysis
    extracted_text = db.Column(Text)  # Text extracted from document
    ai_analysis = db.Column(Text)  # AI analysis of document content
    
    # Status
    is_processed = db.Column(Boolean, default=False)
    upload_complete = db.Column(Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow)
    processed_at = db.Column(DateTime)
    
    # Relationships
    case = relationship('Case', back_populates='documents')
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'

class CourtLocation(db.Model):
    """Court location data for Canadian courts"""
    __tablename__ = 'court_locations'
    
    id = db.Column(Integer, primary_key=True)
    
    # Location information
    name = db.Column(String(200), nullable=False)
    court_type = db.Column(String(100), nullable=False)  # criminal, family, civil, child_protection
    address = db.Column(Text, nullable=False)
    city = db.Column(String(100), nullable=False)
    province = db.Column(String(50), nullable=False)
    postal_code = db.Column(String(10))
    phone = db.Column(String(20))
    website = db.Column(String(200))
    
    # Service area
    postal_code_prefixes = db.Column(Text)  # JSON array of postal code prefixes served
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CourtLocation {self.name}>'