"""
Push Notification System for SmartDispute.ai
Handles deadline reminders, payment notifications, and case updates
"""

import os
import logging
from datetime import datetime, timedelta
from models import User, Case, Document, db
from flask import current_app
from flask_login import login_required, current_user
import json

class NotificationManager:
    def __init__(self):
        self.notification_channels = ['email', 'sms', 'push']
        self.templates = self.load_notification_templates()
    
    def load_notification_templates(self):
        """Load notification templates for different types"""
        return {
            'deadline_reminder': {
                'email': {
                    'subject': 'Legal Deadline Reminder - {case_title}',
                    'body': 'Your case "{case_title}" has an upcoming deadline on {deadline_date}. Action required: {required_action}'
                },
                'sms': 'SmartDispute: Legal deadline {deadline_date} for case "{case_title}". Action: {required_action}',
                'push': {
                    'title': 'Legal Deadline Reminder',
                    'body': 'Case "{case_title}" deadline: {deadline_date}'
                }
            },
            'payment_reminder': {
                'email': {
                    'subject': 'Payment Required - SmartDispute.ai',
                    'body': 'Your subscription requires payment to continue accessing premium features. Amount: ${amount} CAD'
                },
                'sms': 'SmartDispute: Payment of ${amount} CAD required to maintain access.',
                'push': {
                    'title': 'Payment Required',
                    'body': 'Subscription payment of ${amount} CAD needed'
                }
            },
            'case_update': {
                'email': {
                    'subject': 'Case Update - {case_title}',
                    'body': 'Your case "{case_title}" has been updated. New merit score: {merit_score}%. Next actions: {next_actions}'
                },
                'sms': 'SmartDispute: Case "{case_title}" updated. Merit: {merit_score}%',
                'push': {
                    'title': 'Case Updated',
                    'body': '"{case_title}" - Merit: {merit_score}%'
                }
            },
            'document_ready': {
                'email': {
                    'subject': 'Legal Documents Ready - {case_title}',
                    'body': 'Your court documents for "{case_title}" are ready for download and filing.'
                },
                'sms': 'SmartDispute: Documents ready for case "{case_title}"',
                'push': {
                    'title': 'Documents Ready',
                    'body': 'Court forms ready for "{case_title}"'
                }
            }
        }
    
    def create_notification(self, user_id, notification_type, channel, data, scheduled_time=None):
        """Create a new notification"""
        try:
            notification = {
                'id': self.generate_notification_id(),
                'user_id': user_id,
                'type': notification_type,
                'channel': channel,
                'data': data,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                'sent_at': None
            }
            
            # Store in database (you'll need to create a notifications table)
            self.save_notification(notification)
            
            # Send immediately if no schedule time
            if not scheduled_time:
                self.send_notification(notification)
            
            return notification['id']
            
        except Exception as e:
            logging.error(f"Error creating notification: {e}")
            return None
    
    def generate_notification_id(self):
        """Generate unique notification ID"""
        import uuid
        return str(uuid.uuid4())
    
    def save_notification(self, notification):
        """Save notification to database"""
        # This would save to a notifications table
        # For now, we'll log it
        logging.info(f"Notification saved: {notification['type']} for user {notification['user_id']}")
    
    def send_notification(self, notification):
        """Send notification through appropriate channel"""
        try:
            channel = notification['channel']
            
            if channel == 'email':
                self.send_email_notification(notification)
            elif channel == 'sms':
                self.send_sms_notification(notification)
            elif channel == 'push':
                self.send_push_notification(notification)
            
            # Update notification status
            notification['status'] = 'sent'
            notification['sent_at'] = datetime.now().isoformat()
            
        except Exception as e:
            logging.error(f"Error sending notification: {e}")
            notification['status'] = 'failed'
    
    def send_email_notification(self, notification):
        """Send email notification"""
        template = self.templates[notification['type']]['email']
        subject = template['subject'].format(**notification['data'])
        body = template['body'].format(**notification['data'])
        
        # Integration with email service (SendGrid, etc.)
        logging.info(f"Email sent: {subject} to user {notification['user_id']}")
    
    def send_sms_notification(self, notification):
        """Send SMS notification"""
        template = self.templates[notification['type']]['sms']
        message = template.format(**notification['data'])
        
        # Integration with SMS service (Twilio, etc.)
        logging.info(f"SMS sent: {message} to user {notification['user_id']}")
    
    def send_push_notification(self, notification):
        """Send push notification"""
        template = self.templates[notification['type']]['push']
        title = template['title']
        body = template['body'].format(**notification['data'])
        
        # Integration with push service (Firebase Cloud Messaging, etc.)
        logging.info(f"Push notification sent: {title} - {body} to user {notification['user_id']}")
    
    def schedule_deadline_reminders(self, case_id):
        """Schedule deadline reminders for a case"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return
            
            # Calculate deadline dates (example logic)
            filing_deadline = datetime.now() + timedelta(days=30)
            reminder_dates = [
                filing_deadline - timedelta(days=7),  # 1 week before
                filing_deadline - timedelta(days=3),  # 3 days before
                filing_deadline - timedelta(days=1)   # 1 day before
            ]
            
            for reminder_date in reminder_dates:
                if reminder_date > datetime.now():
                    data = {
                        'case_title': case.case_title,
                        'deadline_date': filing_deadline.strftime('%B %d, %Y'),
                        'required_action': 'File court documents'
                    }
                    
                    # Schedule for all preferred channels
                    user = User.query.get(case.user_id)
                    preferred_channels = getattr(user, 'notification_preferences', ['email'])
                    
                    for channel in preferred_channels:
                        self.create_notification(
                            user_id=case.user_id,
                            notification_type='deadline_reminder',
                            channel=channel,
                            data=data,
                            scheduled_time=reminder_date
                        )
                        
        except Exception as e:
            logging.error(f"Error scheduling deadline reminders: {e}")
    
    def notify_case_update(self, case_id, merit_score, next_actions):
        """Notify user of case updates"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return
            
            data = {
                'case_title': case.case_title,
                'merit_score': merit_score,
                'next_actions': ', '.join(next_actions[:2])  # First 2 actions
            }
            
            user = User.query.get(case.user_id)
            preferred_channels = getattr(user, 'notification_preferences', ['email'])
            
            for channel in preferred_channels:
                self.create_notification(
                    user_id=case.user_id,
                    notification_type='case_update',
                    channel=channel,
                    data=data
                )
                
        except Exception as e:
            logging.error(f"Error sending case update notification: {e}")
    
    def notify_payment_required(self, user_id, amount):
        """Notify user that payment is required"""
        try:
            data = {
                'amount': f"{amount:.2f}"
            }
            
            user = User.query.get(user_id)
            preferred_channels = getattr(user, 'notification_preferences', ['email'])
            
            for channel in preferred_channels:
                self.create_notification(
                    user_id=user_id,
                    notification_type='payment_reminder',
                    channel=channel,
                    data=data
                )
                
        except Exception as e:
            logging.error(f"Error sending payment notification: {e}")
    
    def notify_documents_ready(self, case_id):
        """Notify user that documents are ready"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return
            
            data = {
                'case_title': case.case_title
            }
            
            user = User.query.get(case.user_id)
            preferred_channels = getattr(user, 'notification_preferences', ['email'])
            
            for channel in preferred_channels:
                self.create_notification(
                    user_id=case.user_id,
                    notification_type='document_ready',
                    channel=channel,
                    data=data
                )
                
        except Exception as e:
            logging.error(f"Error sending document ready notification: {e}")

# Global instance
notification_manager = NotificationManager()

def init_notification_system(app):
    """Initialize notification system with Flask app"""
    @app.route('/notification-preferences', methods=['GET', 'POST'])
    def notification_preferences():
        """User notification preferences page"""
        from flask import render_template, request, redirect, url_for, flash
        from flask_login import login_required, current_user
        
        if request.method == 'POST':
            preferences = request.form.getlist('channels')
            # Save preferences to user model
            current_user.notification_preferences = preferences
            db.session.commit()
            flash('Notification preferences updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        return render_template('notification_preferences.html')
    
    app.logger.info("Notification system initialized")
    return notification_manager