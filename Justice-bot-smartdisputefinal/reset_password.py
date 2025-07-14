from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    if user:
        user.set_password('password123')
        db.session.commit()
        print('Password reset for testuser to "password123"')
    else:
        print('User "testuser" not found')