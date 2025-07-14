"""
Payment Routes for SmartDispute.ai

This module handles all payment-related routes including PayPal integration.
"""

import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from models import Payment
from app import db

# Create blueprint
payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/options', methods=['GET'])
@login_required
def payment_options():
    """Display payment options page with service selection"""
    return render_template('payment_options.html')

@payment_bp.route('/thankyou', methods=['GET'])
@login_required
def payment_thankyou():
    """Display payment thank you page"""
    return render_template('payment_thankyou.html')

@payment_bp.route('/process', methods=['POST'])
@login_required
def process_payment():
    """Process PayPal payment when client-side payment is complete"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    order_id = data.get('order_id')
    payer_id = data.get('payer_id')
    payer_email = data.get('payer_email')
    amount = data.get('amount')
    selected_service = data.get('selected_service', 'Single Document')
    
    if not order_id or not amount:
        return jsonify({'success': False, 'error': 'Missing payment information'}), 400
    
    try:
        # Record payment in database
        new_payment = Payment(
            user_id=current_user.id,
            payment_provider='PayPal',
            payment_id=order_id,
            amount=float(amount),
            currency='USD',
            status='completed',
            payment_type='document' if float(amount) == 5.00 else 'subscription',
            service_details={
                'order_id': order_id,
                'payer_id': payer_id,
                'payer_email': payer_email,
                'amount': amount,
                'selected_service': selected_service,
                'payment_date': None  # Will be set by PayPal
            }
        )
        
        db.session.add(new_payment)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'payment_id': new_payment.id,
            'redirect_url': url_for('payment.payment_thankyou')
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing payment: {str(e)}")
        return jsonify({'success': False, 'error': 'Server error processing payment'}), 500

@payment_bp.route('/success', methods=['GET'])
@login_required
def payment_success():
    """Handle redirect from PayPal success"""
    order_id = request.args.get('order_id', '')
    
    if not order_id:
        flash('Payment information is missing.', 'warning')
    else:
        flash('Payment successful! Thank you for your purchase.', 'success')
    
    return redirect(url_for('payment.payment_thankyou'))

@payment_bp.route('/cancel', methods=['GET'])
@login_required
def payment_cancel():
    """Handle PayPal payment cancellation"""
    flash('Payment was cancelled. Your card has not been charged.', 'info')
    return redirect(url_for('dashboard'))

# Main function to register payment routes
def register_payment_routes(app):
    """
    Register all payment routes with the Flask app
    This function is called from main.py
    """
    # Check if payment routes are already registered
    if hasattr(app, '_payment_routes_registered') and app._payment_routes_registered:
        app.logger.info("Payment routes already registered, skipping")
        return app
        
    app.logger.info("Registering payment routes")
    init_payment_routes(app)
    
    # Mark payment routes as registered
    app._payment_routes_registered = True
    return app

def init_payment_routes(app):
    """Register payment routes with the app"""
    app.register_blueprint(payment_bp)
    
    # Make PayPal client ID available to all templates
    @app.context_processor
    def inject_paypal_client_id():
        return {
            'paypal_client_id': os.environ.get('PAYPAL_CLIENT_ID', 
                                              'Aa2wlVSlsfPeKRT-HoZx7zBiC3wrF4gpRNkNWgryYsnDcrJJo43Cwu0VCIZAjAVogiEGrMUDoH5TkiXj')
        }