#!/usr/bin/env python3
# Database user diagnostic tool for SmartDispute.ai

import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras

# Get PostgreSQL connection string from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Fix common issue with PostgreSQL URLs from Heroku/some PaaS providers
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not set")
    sys.exit(1)

# Connect to the database
conn = None
try:
    print(f"Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL, sslmode='prefer')
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print("Connected successfully!")
    
    # Check if users table exists
    cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='users')")
    if not cursor.fetchone()[0]:
        print("Error: 'users' table does not exist")
        sys.exit(1)
    
    # Get all users
    cursor.execute("SELECT id, email, username, password_hash FROM users")
    users = cursor.fetchall()
    
    print(f"Found {len(users)} users in the database:")
    for user in users:
        print(f"ID: {user['id']}, Email: {user['email']}, Username: {user['username']}")
        print(f"  Password hash length: {len(user['password_hash']) if user['password_hash'] else 0}")
        
        # Check if hash format is correct
        password_hash = user['password_hash']
        if password_hash:
            try:
                # Werkzeug password hashes start with 'pbkdf2:sha256:'
                if not password_hash.startswith('pbkdf2:sha256:'):
                    print(f"  Warning: Password hash format seems incorrect - doesn't start with 'pbkdf2:sha256:'")
                    print(f"  Hash starts with: {password_hash[:20]}...")
                else:
                    print(f"  Hash format appears correct")
                    
                # Try validating with a test password
                try:
                    result = check_password_hash(password_hash, "test_password")
                    print(f"  Hash can be processed by check_password_hash: Yes")
                except Exception as e:
                    print(f"  Error validating hash with check_password_hash: {str(e)}")
            except Exception as e:
                print(f"  Error analyzing password hash: {str(e)}")
        else:
            print(f"  Warning: User has no password hash")
        
        print("")
    
    # Test hashing function
    print("\nTesting password hashing:")
    test_passwords = ["password123!", "User123!", "complex_P@ssw0rd"]
    for password in test_passwords:
        hash = generate_password_hash(password)
        valid = check_password_hash(hash, password)
        print(f"Password: {password}")
        print(f"Generated hash: {hash[:25]}...")
        print(f"Hash length: {len(hash)}")
        print(f"Validation: {valid}\n")
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)
finally:
    if conn:
        conn.close()
        print("Database connection closed")
