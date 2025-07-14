#!/usr/bin/env python3
"""
User Management Workflow for SmartDispute.ai
Automates user onboarding, test account creation, and user analytics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Case, Document
from admin_system import create_test_accounts, generate_secure_password
import logging
from datetime import datetime, timedelta
import csv

class UserManagementWorkflow:
    def __init__(self):
        self.app = app
        
    def daily_user_report(self):
        """Generate daily user activity report"""
        with self.app.app_context():
            # Get user statistics
            total_users = User.query.count()
            real_users = User.query.filter_by(is_test_user=False).count()
            test_users = User.query.filter_by(is_test_user=True).count()
            
            # Users registered in last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            new_users_today = User.query.filter(User.created_at >= yesterday).count()
            
            # Active users (logged in last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            active_users = User.query.filter(User.last_login >= week_ago).count() if hasattr(User, 'last_login') else 0
            
            # Cases created today
            cases_today = Case.query.filter(Case.created_at >= yesterday).count() if hasattr(Case, 'created_at') else 0
            
            report = f"""
SmartDispute.ai Daily User Report - {datetime.now().strftime('%Y-%m-%d')}
================================================================

📊 USER STATISTICS:
• Total Users: {total_users}
• Real Users: {real_users}/1000 (Pilot Program)
• Test Users: {test_users}
• New Users Today: {new_users_today}
• Active Users (7 days): {active_users}

📁 ACTIVITY:
• Cases Created Today: {cases_today}
• Pilot Program Status: {(real_users/1000)*100:.1f}% full

🚨 ALERTS:
"""
            
            # Check if approaching pilot limit
            if real_users >= 950:
                report += "• WARNING: Approaching 1000 user pilot limit!\n"
            elif real_users >= 900:
                report += "• NOTICE: 90% of pilot program capacity reached\n"
            
            # Save report
            os.makedirs('reports', exist_ok=True)
            filename = f"reports/daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(filename, 'w') as f:
                f.write(report)
                
            print(report)
            return report
    
    def create_bulk_test_users(self, count=10):
        """Create multiple test users for testing"""
        with self.app.app_context():
            users_created = []
            for i in range(count):
                try:
                    # Create test user with Canadian theme
                    provinces = ['ON', 'BC', 'AB', 'QC', 'NS', 'NB', 'MB', 'SK', 'PE', 'NL']
                    cities = ['Toronto', 'Vancouver', 'Calgary', 'Montreal', 'Halifax', 'Winnipeg']
                    legal_issues = ['Family Law', 'Criminal Defense', 'Civil Rights', 'Employment', 'Housing']
                    
                    user_data = {
                        'first_name': f'TestUser{i+1}',
                        'last_name': 'Charter',
                        'email': f'testuser{i+1}@smartdispute.ca',
                        'province': provinces[i % len(provinces)],
                        'city': cities[i % len(cities)],
                        'legal_issue_type': legal_issues[i % len(legal_issues)],
                        'is_test_user': True,
                        'pilot_consent': True
                    }
                    
                    password = generate_secure_password()
                    
                    # Create user account
                    user = User(**user_data)
                    user.set_password(password)
                    db.session.add(user)
                    db.session.commit()
                    
                    users_created.append({
                        'email': user_data['email'],
                        'password': password,
                        'name': f"{user_data['first_name']} {user_data['last_name']}"
                    })
                    
                except Exception as e:
                    logging.error(f"Error creating test user {i+1}: {e}")
                    continue
            
            # Save credentials to file
            filename = f"test_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['name', 'email', 'password'])
                writer.writeheader()
                writer.writerows(users_created)
            
            print(f"Created {len(users_created)} test users. Credentials saved to {filename}")
            return users_created
    
    def cleanup_inactive_test_users(self, days=30):
        """Remove test users inactive for specified days"""
        with self.app.app_context():
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Find inactive test users
            inactive_users = User.query.filter(
                User.is_test_user == True,
                User.last_login < cutoff_date if hasattr(User, 'last_login') else User.created_at < cutoff_date
            ).all()
            
            deleted_count = 0
            for user in inactive_users:
                try:
                    # Delete associated data first
                    Case.query.filter_by(user_id=user.id).delete()
                    Document.query.filter_by(user_id=user.id).delete()
                    
                    # Delete user
                    db.session.delete(user)
                    deleted_count += 1
                    
                except Exception as e:
                    logging.error(f"Error deleting user {user.email}: {e}")
                    continue
            
            db.session.commit()
            print(f"Cleaned up {deleted_count} inactive test users")
            return deleted_count
    
    def export_user_analytics(self):
        """Export comprehensive user analytics for Teresa"""
        with self.app.app_context():
            # Get all real users (excluding test users)
            real_users = User.query.filter_by(is_test_user=False).all()
            
            analytics_data = []
            for user in real_users:
                user_cases = Case.query.filter_by(user_id=user.id).count() if hasattr(Case, 'user_id') else 0
                user_docs = Document.query.filter_by(user_id=user.id).count() if hasattr(Document, 'user_id') else 0
                
                analytics_data.append({
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'province': getattr(user, 'province', 'Unknown'),
                    'city': getattr(user, 'city', 'Unknown'),
                    'legal_issue': getattr(user, 'legal_issue_type', 'Unknown'),
                    'joined_date': user.created_at.strftime('%Y-%m-%d') if hasattr(user, 'created_at') else 'Unknown',
                    'cases_count': user_cases,
                    'documents_count': user_docs,
                    'pilot_consent': getattr(user, 'pilot_consent', False)
                })
            
            # Export to CSV
            filename = f"user_analytics_{datetime.now().strftime('%Y%m%d')}.csv"
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['name', 'email', 'province', 'city', 'legal_issue', 'joined_date', 'cases_count', 'documents_count', 'pilot_consent']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(analytics_data)
            
            print(f"User analytics exported to {filename}")
            return filename

def main():
    """Run user management workflow based on command line argument"""
    if len(sys.argv) < 2:
        print("Usage: python user_management.py [daily_report|create_test_users|cleanup|analytics]")
        return
    
    workflow = UserManagementWorkflow()
    command = sys.argv[1]
    
    if command == 'daily_report':
        workflow.daily_user_report()
    elif command == 'create_test_users':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        workflow.create_bulk_test_users(count)
    elif command == 'cleanup':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        workflow.cleanup_inactive_test_users(days)
    elif command == 'analytics':
        workflow.export_user_analytics()
    else:
        print("Unknown command. Available: daily_report, create_test_users, cleanup, analytics")

if __name__ == '__main__':
    main()