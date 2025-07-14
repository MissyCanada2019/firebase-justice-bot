"""
Create admin account for testing
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin():
    """Create admin account for immediate testing"""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email="admin@smartdispute.ca").first()
        
        if not admin:
            admin = User(
                email="admin@smartdispute.ca",
                password=generate_password_hash("Admin123"),
                is_admin=True,
                first_name="Admin",
                last_name="User",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin account created: admin@smartdispute.ca / Admin123")
        else:
            print("✅ Admin account already exists")

        # Create test user account
        test_user = User.query.filter_by(email="test@smartdispute.ca").first()
        
        if not test_user:
            test_user = User(
                email="test@smartdispute.ca",
                password=generate_password_hash("Test123"),
                is_admin=False,
                first_name="Test",
                last_name="User",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test account created: test@smartdispute.ca / Test123")
        else:
            print("✅ Test account already exists")

if __name__ == "__main__":
    create_admin()