#!/usr/bin/env python3
"""
Direct script to create clean test users for real data accumulation
"""
import os
import sys
sys.path.append('/home/runner/workspace')

from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor

def create_clean_test_users():
    """Create clean test users directly in database"""
    
    # Database connection
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return
    
    test_users = [
        {'email': 'user1@test.ca', 'password': 'Test123!', 'first_name': 'Alex', 'last_name': 'Smith'},
        {'email': 'user2@test.ca', 'password': 'Test123!', 'first_name': 'Jordan', 'last_name': 'Williams'},
        {'email': 'user3@test.ca', 'password': 'Test123!', 'first_name': 'Taylor', 'last_name': 'Brown'},
        {'email': 'user4@test.ca', 'password': 'Test123!', 'first_name': 'Casey', 'last_name': 'Davis'},
        {'email': 'user5@test.ca', 'password': 'Test123!', 'first_name': 'Riley', 'last_name': 'Johnson'},
        {'email': 'user6@test.ca', 'password': 'Test123!', 'first_name': 'Morgan', 'last_name': 'Wilson'},
        {'email': 'user7@test.ca', 'password': 'Test123!', 'first_name': 'Sam', 'last_name': 'Martinez'},
        {'email': 'user8@test.ca', 'password': 'Test123!', 'first_name': 'Quinn', 'last_name': 'Anderson'}
    ]
    
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        print("Creating clean test user accounts for real data accumulation...")
        print("=" * 60)
        
        created_users = []
        
        for user_data in test_users:
            # Check if user exists
            cur.execute("SELECT id FROM users WHERE email = %s", (user_data['email'],))
            existing = cur.fetchone()
            
            if not existing:
                # Create user
                user_uuid = str(uuid.uuid4())
                password_hash = generate_password_hash(user_data['password'])
                now = datetime.utcnow()
                
                cur.execute("""
                    INSERT INTO users (
                        email, password, first_name, last_name, is_admin,
                        created_at, updated_at, email_verified
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_data['email'],
                    password_hash,
                    user_data['first_name'],
                    user_data['last_name'],
                    False,
                    now,
                    now,
                    True
                ))
                
                created_users.append(user_data)
                print(f"✅ Created: {user_data['email']} - {user_data['first_name']} {user_data['last_name']}")
            else:
                print(f"🔄 Already exists: {user_data['email']}")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("TEST USER LOGIN INFORMATION")
        print("=" * 60)
        
        for user in created_users:
            print(f"""
Email: {user['email']}
Password: {user['password']}
Name: {user['first_name']} {user['last_name']}
Status: Clean account ready for real data upload
            """)
        
        if not created_users:
            print("All test users already exist. Here are the credentials:")
            for user in test_users:
                print(f"""
Email: {user['email']}
Password: {user['password']}
Name: {user['first_name']} {user['last_name']}
Status: Clean account ready for real data upload
                """)
        
        print("=" * 60)
        print("ADMIN ACCOUNT")
        print("=" * 60)
        print("""
Email: admin@smartdispute.ca
Password: Admin123
Name: Admin User
Access: Full admin dashboard and user management
        """)
        
        print("=" * 60)
        print("REAL DATA ACCUMULATION STRATEGY")
        print("=" * 60)
        print("""
CLEAN SLATE APPROACH:
- Each account starts completely empty
- Users upload their own real legal documents
- Cases created from actual legal situations
- Evidence uploaded from real scenarios

HOW TO USE:
1. Share different login credentials with different testers
2. Each person logs in and creates cases for their real legal needs
3. Upload actual documents (anonymized if needed)
4. Use genuine legal scenarios for authentic testing

DATABASE VALUE:
- Every document upload improves AI analysis accuracy
- Real case data enhances legal recommendations
- Authentic interactions train the system better
- Genuine usage patterns optimize features

PRIVACY & SECURITY:
- All data encrypted in PostgreSQL cloud database
- User accounts completely isolated from each other
- No cross-user data visibility
- Secure authentication and session management
        """)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_clean_test_users()