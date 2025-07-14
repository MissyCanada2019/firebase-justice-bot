"""
Enhanced Payment Routes for SmartDispute.ai
Includes PayPal and e-transfer integration with teresa@justice-bot.com email notifications
"""
import os
import uuid
import logging
import smtplib
from datetime import datetime, timedelta
from decimal import Decimal
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import db
from models import Payment, User, Case
import requests

payment_bp = Blueprint('payment_enhanced', __name__, url_prefix='/payment')
logger = logging.getLogger(__name__)

# Payment configuration
PAYMENT_NOTIFICATION_EMAIL = "teresa@justice-bot.com"
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')

# E-transfer configuration
ETRANSFER_EMAIL = "payments@smartdispute.ai"
ETRANSFER_SECURITY_QUESTION = "What is the name of our legal platform?"
ETRANSFER_SECURITY_ANSWER = "SmartDispute"

def send_payment_notification(payment_data, payment_type):
    """Send payment notification email to teresa@justice-bot.com"""
    try:
        subject = f"New {payment_type} Payment Received - SmartDispute.ai"
        
        body = f"""
New payment received on SmartDispute.ai:

Payment Details:
- Payment ID: {payment_data.get('payment_id')}
- Amount: ${payment_data.get('amount')}
- Currency: {payment_data.get('currency', 'CAD')}
- Payment Type: {payment_type}
- User: {payment_data.get('user_email')}
- Service: {payment_data.get('service_description')}
- Status: {payment_data.get('status')}
- Date: {payment_data.get('created_at')}

Transaction Reference: {payment_data.get('transaction_reference')}

Please process this payment and update the user's account accordingly.

Best regards,
SmartDispute.ai Automated System
        """
        
        logger.info(f"Payment notification sent to {PAYMENT_NOTIFICATION_EMAIL}")
        logger.info(f"Payment details: {payment_data}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to send payment notification: {e}")
        return False

@payment_bp.route('/options')
@login_required
def payment_options():
    """Display payment options page"""
    service_type = request.args.get('service', 'document_generation')
    case_id = request.args.get('case_id')
    
    # Service pricing
    pricing = {
        'document_generation': {'amount': 29.99, 'description': 'Legal Document Generation'},
        'case_analysis': {'amount': 49.99, 'description': 'Case Merit Analysis'},
        'full_service': {'amount': 99.99, 'description': 'Complete Legal Package'},
        'consultation': {'amount': 149.99, 'description': 'Legal Consultation'},
        'premium_support': {'amount': 199.99, 'description': 'Premium Support Package'}
    }
    
    service_info = pricing.get(service_type, pricing['document_generation'])
    
    return render_template('payment/options.html',
                         service_info=service_info,
                         service_type=service_type,
                         case_id=case_id,
                         paypal_client_id=PAYPAL_CLIENT_ID,
                         etransfer_email=ETRANSFER_EMAIL)

@payment_bp.route('/paypal/create', methods=['POST'])
@login_required
def create_paypal_payment():
    """Create PayPal payment"""
    try:
        service_type = request.form.get('service_type')
        case_id = request.form.get('case_id')
        amount = Decimal(request.form.get('amount', '0'))
        
        payment = Payment(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            amount=amount,
            currency='CAD',
            payment_method='paypal',
            status='pending',
            service_type=service_type,
            case_id=case_id,
            transaction_reference=f"PP_{int(datetime.now().timestamp())}",
            created_at=datetime.utcnow()
        )
        
        db.session.add(payment)
        db.session.commit()
        
        session['pending_payment_id'] = payment.id
        
        return jsonify({
            'success': True,
            'payment_id': payment.id,
            'amount': str(amount),
            'currency': 'CAD'
        })
        
    except Exception as e:
        logger.error(f"PayPal payment creation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@payment_bp.route('/paypal/complete', methods=['POST'])
@login_required
def complete_paypal_payment():
    """Complete PayPal payment"""
    try:
        paypal_payment_id = request.form.get('paymentID')
        payer_id = request.form.get('payerID')
        payment_id = session.get('pending_payment_id')
        
        if not payment_id:
            return jsonify({'success': False, 'error': 'No pending payment found'}), 400
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'success': False, 'error': 'Payment not found'}), 404
        
        payment.status = 'completed'
        payment.paypal_payment_id = paypal_payment_id
        payment.paypal_payer_id = payer_id
        payment.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        payment_data = {
            'payment_id': payment.id,
            'amount': str(payment.amount),
            'currency': payment.currency,
            'user_email': current_user.email,
            'service_description': payment.service_type,
            'status': payment.status,
            'created_at': payment.created_at.isoformat(),
            'transaction_reference': payment.transaction_reference
        }
        
        send_payment_notification(payment_data, 'PayPal')
        
        session.pop('pending_payment_id', None)
        
        flash('Payment completed successfully!', 'success')
        return redirect(url_for('payment_enhanced.success', payment_id=payment.id))
        
    except Exception as e:
        logger.error(f"PayPal payment completion failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@payment_bp.route('/etransfer/initiate', methods=['POST'])
@login_required
def initiate_etransfer():
    """Initiate e-transfer payment"""
    try:
        service_type = request.form.get('service_type')
        case_id = request.form.get('case_id')
        amount = Decimal(request.form.get('amount', '0'))
        
        payment = Payment(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            amount=amount,
            currency='CAD',
            payment_method='etransfer',
            status='pending',
            service_type=service_type,
            case_id=case_id,
            transaction_reference=f"ET_{int(datetime.now().timestamp())}",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.session.add(payment)
        db.session.commit()
        
        payment_data = {
            'payment_id': payment.id,
            'amount': str(payment.amount),
            'currency': payment.currency,
            'user_email': current_user.email,
            'service_description': payment.service_type,
            'status': payment.status,
            'created_at': payment.created_at.isoformat(),
            'transaction_reference': payment.transaction_reference
        }
        
        send_payment_notification(payment_data, 'E-Transfer')
        
        flash('E-transfer payment initiated. Please check your email for instructions.', 'info')
        return redirect(url_for('payment_enhanced.etransfer_instructions', payment_id=payment.id))
        
    except Exception as e:
        logger.error(f"E-transfer initiation failed: {e}")
        flash('Failed to initiate e-transfer payment. Please try again.', 'error')
        return redirect(url_for('payment_enhanced.payment_options'))

@payment_bp.route('/etransfer/instructions/<payment_id>')
@login_required
def etransfer_instructions(payment_id):
    """Display e-transfer instructions"""
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.user_id != current_user.id:
        flash('Unauthorized access to payment.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('payment/etransfer_instructions.html',
                         payment=payment,
                         etransfer_email=ETRANSFER_EMAIL,
                         security_question=ETRANSFER_SECURITY_QUESTION,
                         security_answer=ETRANSFER_SECURITY_ANSWER)

@payment_bp.route('/success/<payment_id>')
@login_required
def success(payment_id):
    """Payment success page"""
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.user_id != current_user.id:
        flash('Unauthorized access to payment.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('payment/success.html', payment=payment)

@payment_bp.route('/history')
@login_required
def history():
    """Display payment history"""
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    return render_template('payment/history.html', payments=payments)