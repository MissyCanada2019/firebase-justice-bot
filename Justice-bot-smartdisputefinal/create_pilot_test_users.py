"""
Pilot Test User Creation Utility
Creates test users to demonstrate the 1000 user tracking system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash
import random

def create_pilot_test_users(count=5):
    """Create test users for the pilot program"""
    
    with app.app_context():
        # Get current real user count
        real_user_count = User.query.filter_by(is_free_user=True, is_test_user=False).count()
        
        print(f"Current real users in pilot program: {real_user_count}/1000")
        
        # Sample Canadian cities and provinces
        canadian_locations = [
            ("Toronto", "ON", "M5H 2N2"),
            ("Vancouver", "BC", "V6B 1A1"),
            ("Montreal", "QC", "H3A 0G4"),
            ("Calgary", "AB", "T2P 1J9"),
            ("Ottawa", "ON", "K1A 0A6"),
            ("Edmonton", "AB", "T5J 2R7"),
            ("Winnipeg", "MB", "R3C 0V8"),
            ("Halifax", "NS", "B3J 3K9"),
            ("Saskatoon", "SK", "S7K 3J7"),
            ("Victoria", "BC", "V8W 1P6")
        ]
        
        legal_issues = [
            "housing", "employment", "consumer", "family", 
            "criminal", "immigration", "disability", "human_rights"
        ]
        
        created_users = []
        
        for i in range(count):
            city, province, postal_code = random.choice(canadian_locations)
            legal_issue = random.choice(legal_issues)
            
            # Create test user
            test_user = User(
                first_name=f"TestUser{real_user_count + i + 1}",
                last_name="Pilot",
                email=f"testuser{real_user_count + i + 1}@smartdispute-pilot.com",
                phone=f"(416) 555-{1000 + i:04d}",
                address=f"{100 + i} Test Street",
                city=city,
                province=province,
                postal_code=postal_code,
                legal_issue_type=legal_issue,
                is_free_user=True,
                is_test_user=True,  # Flag as test user
                free_user_number=real_user_count + i + 1,
                pilot_consent=True,
                email_verified=True
            )
            test_user.set_password("TestPassword123!")
            
            db.session.add(test_user)
            created_users.append(test_user)
        
        db.session.commit()
        
        print(f"Created {len(created_users)} test users:")
        for user in created_users:
            print(f"  - {user.first_name} {user.last_name} (#{user.free_user_number}) - {user.city}, {user.province} - {user.legal_issue_type}")
        
        # Updated count
        new_real_count = User.query.filter_by(is_free_user=True, is_test_user=False).count()
        new_test_count = User.query.filter_by(is_free_user=True, is_test_user=True).count()
        
        print(f"\nPilot program status:")
        print(f"  Real users: {new_real_count}/1000")
        print(f"  Test users: {new_test_count}")
        print(f"  Total: {new_real_count + new_test_count}")
        
        return created_users

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    create_pilot_test_users(count)