from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
from sqlalchemy import Index, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID, TSVECTOR
from sqlalchemy.ext.mutable import MutableDict
import uuid

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), default='user', index=True)  # user or admin
    created_at = db.Column(db.TIMESTAMP, server_default=func.now(), index=True)
    last_login = db.Column(db.TIMESTAMP, nullable=True)
    
    # User settings/preferences - keeping this from previous version
    settings = db.Column(MutableDict.as_mutable(JSONB), nullable=True, default=lambda: {
        "notifications": True,
        "language": "en",
        "theme": "light",
        "high_contrast": False,
        "text_size": "medium"
    })
    
    # Relationships
    disputes = db.relationship('Dispute', backref='user', lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_reset_token(self):
        """Generate a token for password reset"""
        return str(uuid.uuid4())
    
    def get_id(self):
        """Override get_id from UserMixin to return string representation of UUID"""
        return str(self.id)

class Dispute(db.Model):
    __tablename__ = "disputes"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    case_type = db.Column(db.String(100), nullable=False, index=True)  # housing, credit, CAS, police, etc.
    status = db.Column(db.String(50), default='draft', index=True)  # draft, submitted, closed
    created_at = db.Column(db.TIMESTAMP, server_default=func.now(), index=True)
    updated_at = db.Column(db.TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Adding a title field which is useful for display
    title = db.Column(db.String(255), nullable=True)
    
    # Full-text search vector for PostgreSQL 
    search_vector = db.Column(TSVECTOR, nullable=True)
    
    # Relationships
    documents = db.relationship('Document', backref='dispute', lazy=True, cascade="all, delete-orphan")
    merit_score = db.relationship('CaseMeritScore', backref='dispute', uselist=False, cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_dispute_user_id', 'user_id'),
        Index('ix_dispute_search_vector', 'search_vector', postgresql_using='gin'),
    )

class Document(db.Model):
    __tablename__ = "documents"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = db.Column(UUID(as_uuid=True), db.ForeignKey('disputes.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(50), nullable=True, index=True)  # upload, generated_form
    created_at = db.Column(db.TIMESTAMP, server_default=func.now(), index=True)
    
    # Keep extracted text from previous version
    extracted_text = db.Column(db.Text, nullable=True)
    
    # Document metadata
    doc_metadata = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    
    # Full-text search vector for PostgreSQL
    search_vector = db.Column(TSVECTOR, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_document_dispute_id', 'dispute_id'),
        Index('ix_document_search_vector', 'search_vector', postgresql_using='gin'),
    )

class Payment(db.Model):
    __tablename__ = "payments"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    payment_provider = db.Column(db.String(50), nullable=True)  # PayPal, Stripe, etc.
    payment_id = db.Column(db.String(255), unique=True, nullable=True)  # Provider's transaction ID
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default='CAD')
    status = db.Column(db.String(50), default='pending', index=True)  # pending, completed, failed
    created_at = db.Column(db.TIMESTAMP, server_default=func.now(), index=True)
    
    # Add payment type from previous version
    payment_type = db.Column(db.String(50), nullable=True, index=True)  # document, subscription, mailing
    
    # Service details from previous version
    service_details = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_payment_user_id', 'user_id'),
        Index('ix_payment_status', 'status'),
        Index('ix_payment_created_at', 'created_at'),
    )

class CaseMeritScore(db.Model):
    __tablename__ = "case_merit_scores"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispute_id = db.Column(UUID(as_uuid=True), db.ForeignKey('disputes.id'), nullable=False, unique=True)
    score = db.Column(db.Integer, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    legal_references = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    
    # Add details JSON field for storing additional analysis
    details = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    
    # Indexes for performance and constraints
    __table_args__ = (
        Index('ix_case_merit_scores_dispute_id', 'dispute_id'),
        db.CheckConstraint('score >= 0 AND score <= 100', name='score_range_check'),
    )

# Chat functionality from previous version
class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    dispute_id = db.Column(UUID(as_uuid=True), db.ForeignKey('disputes.id'), nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    title = db.Column(db.String(200), nullable=True)
    
    # Session data for context management, preferences, etc.
    session_data = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_chat_session_user_id', 'user_id'),
        Index('ix_chat_session_dispute_id', 'dispute_id'),
        Index('ix_chat_session_created_at', 'created_at'),
    )

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chat_sessions.id'), nullable=False)
    is_user = db.Column(db.Boolean, default=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=func.now())
    
    # Additional message data like references, metadata, etc.
    message_data = db.Column(MutableDict.as_mutable(JSONB), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_chat_message_session_id', 'session_id'),
        Index('ix_chat_message_is_user', 'is_user'),
        Index('ix_chat_message_timestamp', 'timestamp'),
    )