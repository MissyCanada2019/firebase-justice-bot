#!/usr/bin/env python3
"""Create a test user for login verification"""

from app import app
from database_fix import db
from models import User

with app.app_context():
    # Check if test user already exists
    test_user = User.query.filter_by(email='test@smartdispute.ai').first()
    
    if not test_user:
        # Create test user
        user = User(
            email='test@smartdispute.ai',
            full_name='Test User',
            province='ON',
            city='Toronto'
        )
        user.set_password('testpass123')
        
        db.session.add(user)
        db.session.commit()
        
        print("✓ Test user created successfully!")
        print("\nLogin credentials:")
        print("Email: test@smartdispute.ai")
        print("Password: testpass123")
    else:
        print("Test user already exists!")
        print("\nLogin credentials:")
        print("Email: test@smartdispute.ai")
        print("Password: testpass123")