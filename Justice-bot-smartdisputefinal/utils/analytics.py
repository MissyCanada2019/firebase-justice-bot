#!/usr/bin/env python3
"""
Analytics Utilities for SmartDispute.ai

This module provides functionality for tracking user interactions,
page views, and other analytics data.
"""
import os
import json
import datetime
import logging
from typing import Dict, Any, Optional
from flask import request, session, g
from decimal import Decimal

from app import db

# Configure logging
logger = logging.getLogger(__name__)

class AnalyticsManager:
    """Manager class for handling analytics data"""
    
    def __init__(self):
        self.initialized = False
        self.tracking_id = os.environ.get('GOOGLE_ANALYTICS_ID')
        
    def init_app(self, app):
        """Initialize analytics with the Flask app"""
        self.initialized = True
        
        @app.before_request
        def track_request():
            """Track each request"""
            if request.endpoint == 'static':
                return
                
            # Store analytics data in g for this request
            g.analytics = {
                'page_view': True,
                'timestamp': datetime.datetime.utcnow(),
                'url': request.path,
                'user_id': session.get('user_id'),
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string,
                'referrer': request.referrer,
            }
        
        @app.after_request
        def save_analytics(response):
            """Save analytics data after each request"""
            if hasattr(g, 'analytics'):
                try:
                    self.save_event(g.analytics)
                except Exception as e:
                    logger.error(f"Error saving analytics: {str(e)}")
            return response
            
    def save_event(self, data: Dict[str, Any]):
        """Save an analytics event to the database"""
        try:
            # Check if analytics table exists, create if not
            self._ensure_analytics_table()
            
            # Insert the analytics event
            sql = """
                INSERT INTO analytics 
                (timestamp, url, user_id, event_type, event_data, ip_address, user_agent, referrer)
                VALUES (:timestamp, :url, :user_id, :event_type, :event_data, :ip_address, :user_agent, :referrer)
            """
            
            # Default event type is page_view
            event_type = data.pop('event_type', 'page_view')
            
            # Prepare data for storing
            params = {
                'timestamp': data.get('timestamp', datetime.datetime.utcnow()),
                'url': data.get('url'),
                'user_id': data.get('user_id'),
                'event_type': event_type,
                'event_data': json.dumps(data, default=self._json_serializer),
                'ip_address': data.get('ip_address'),
                'user_agent': data.get('user_agent'),
                'referrer': data.get('referrer')
            }
            
            # Execute the SQL
            from sqlalchemy import text
            db.session.execute(text(sql), params)
            db.session.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error saving analytics event: {str(e)}")
            db.session.rollback()
            return False
    
    def track_event(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """Track a custom event"""
        if not data:
            data = {}
            
        # Add basic tracking info
        event_data = {
            'event_type': event_type,
            'timestamp': datetime.datetime.utcnow(),
            'url': request.path if request else None,
            'user_id': session.get('user_id') if session else None,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.user_agent.string if request and request.user_agent else None,
            'referrer': request.referrer if request else None,
        }
        
        # Update with custom data
        event_data.update(data)
        
        # Save the event
        return self.save_event(event_data)
        
    def _json_serializer(self, obj):
        """Custom JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Type {type(obj)} not serializable")
        
    def _ensure_analytics_table(self):
        """Ensure the analytics table exists in the database"""
        try:
            # Check if the analytics table exists
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'analytics'
            """)).fetchone()
            
            if not result:
                # Create the analytics table
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS analytics (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        url VARCHAR(255),
                        user_id VARCHAR(255),
                        event_type VARCHAR(50),
                        event_data JSONB,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        referrer TEXT
                    )
                """))
                
                # Create indexes for faster queries
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics (timestamp)
                """))
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics (user_id)
                """))
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics (event_type)
                """))
                
                db.session.commit()
                logger.info("Created analytics table")
                
        except Exception as e:
            logger.error(f"Error creating analytics table: {str(e)}")
            db.session.rollback()

# Create the analytics manager instance
analytics = AnalyticsManager()

# Functions for tracking specific events
def track_login(user_id, login_method="standard"):
    """Track a successful login"""
    return analytics.track_event('login', {
        'user_id': user_id,
        'login_method': login_method
    })

def track_signup(user_id):
    """Track a new user signup"""
    return analytics.track_event('signup', {
        'user_id': user_id
    })

def track_document_upload(user_id, document_id, document_type, file_size):
    """Track a document upload"""
    return analytics.track_event('document_upload', {
        'user_id': user_id,
        'document_id': document_id,
        'document_type': document_type,
        'file_size': file_size
    })

def track_form_generation(user_id, form_id, form_type):
    """Track a form generation"""
    return analytics.track_event('form_generation', {
        'user_id': user_id,
        'form_id': form_id,
        'form_type': form_type
    })

def track_payment(user_id, payment_id, amount, payment_method):
    """Track a payment"""
    return analytics.track_event('payment', {
        'user_id': user_id,
        'payment_id': payment_id,
        'amount': amount,
        'payment_method': payment_method
    })
