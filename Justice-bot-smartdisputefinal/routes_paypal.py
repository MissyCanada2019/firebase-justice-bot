"""
PayPal Payment Routes for SmartDispute.ai

This module contains all the routes related to PayPal payment processing.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import db
from models import Payment, Dispute, Document
from utils.paypal_service import verify_paypal_payment, create_paypal_order, capture_paypal_order

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
paypal_bp = Blueprint('paypal', __name__, url_prefix='/paypal')

# Get PayPal client ID from environment
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')

@paypal_bp.route('/checkout/<string:item_type>/<int:item_id>', methods=['GET'])
@login_required
def checkout(item_type, item_id):
    """
    Display the PayPal checkout page for a specific item
    
    Args:
        item_type (str): Type of item being purchased (document, subscription)
        item_id (int): ID of the item being purchased
    """
    payment_id = str(uuid.uuid4())
    amount = "5.00"  # Default amount
    description = "SmartDispute.ai Document"
    
    # Generate different prices and descriptions based on item type
    if item_type == 'document':
        amount = "5.99"
        description = "Document Generation"
        
    elif item_type == 'subscription':
        if request.args.get('plan') == 'monthly':
            amount = "50.00"
            description = "Monthly Subscription"
        elif request.args.get('plan') == 'yearly':
            amount = "450.00"
            description = "Yearly Subscription"
        elif request.args.get('plan') == 'low_income':
            amount = "25.00"
            description = "Low Income Yearly Subscription"
    
    # Store payment info in session
    session['payment_info'] = {
        'payment_id': payment_id,
        'amount': amount,
        'description': description,
        'item_type': item_type,
        'item_id': item_id
    }
    
    # Render payment template
    return render_template(
        'paypal_payment.html',
        payment_id=payment_id,
        amount=amount,
        description=description,
        item_type=item_type,
        item_id=item_id,
        paypal_client_id=PAYPAL_CLIENT_ID
    )

@paypal_bp.route('/create-order', methods=['POST'])
@login_required
def create_order():
    """Create a PayPal order"""
    try:
        # Get payment info from session
        payment_info = session.get('payment_info', {})
        
        if not payment_info:
            return jsonify({
                'success': False,
                'error': 'Invalid payment session'
            }), 400
        
        # Create order with PayPal
        order_id = create_paypal_order(
            amount=payment_info.get('amount', '5.00'),
            description=payment_info.get('description', 'SmartDispute.ai Payment')
        )
        
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'Failed to create PayPal order'
            }), 500
        
        # Return order ID to client
        return jsonify({
            'success': True,
            'order_id': order_id
        })
    
    except Exception as e:
        logger.error(f"Error creating PayPal order: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Server error creating order'
        }), 500

@paypal_bp.route('/capture-order', methods=['POST'])
@login_required
def capture_payment():
    """Capture a PayPal payment"""
    try:
        # Get request data
        data = request.json
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'Missing order ID'
            }), 400
        
        # Capture payment with PayPal
        capture_details = capture_paypal_order(order_id)
        
        if not capture_details:
            return jsonify({
                'success': False,
                'error': 'Failed to capture payment'
            }), 500
        
        # Get payment info from session
        payment_info = session.get('payment_info', {})
        
        if not payment_info:
            return jsonify({
                'success': False,
                'error': 'Invalid payment session'
            }), 400
        
        # Record payment in database
        new_payment = Payment(
            user_id=current_user.id,
            payment_provider='PayPal',
            payment_id=capture_details.get('capture_id'),
            amount=float(capture_details.get('amount', 0)),
            currency=capture_details.get('currency', 'CAD'),
            status='completed',
            payment_type=payment_info.get('item_type', 'document'),
            service_details={
                'payment_id': payment_info.get('payment_id'),
                'item_type': payment_info.get('item_type'),
                'item_id': payment_info.get('item_id'),
                'description': payment_info.get('description'),
                'paypal_order_id': order_id,
                'paypal_details': capture_details.get('full_response')
            }
        )
        
        db.session.add(new_payment)
        
        # Update item status based on type
        if payment_info.get('item_type') == 'document':
            # Find document and mark as paid
            # Update this to match your actual document model
            item_id = payment_info.get('item_id')
            # document = GeneratedForm.query.get(item_id)
            # if document:
            #     document.is_paid = True
            
        elif payment_info.get('item_type') == 'subscription':
            # Update user subscription
            plan = request.args.get('plan', 'monthly')
            
            if plan == 'monthly':
                current_user.subscription_type = 'unlimited'
                # Set subscription end date to 1 month from now
                # current_user.subscription_end = datetime.utcnow() + timedelta(days=30)
            elif plan == 'yearly':
                current_user.subscription_type = 'unlimited'
                # Set subscription end date to 1 year from now
                # current_user.subscription_end = datetime.utcnow() + timedelta(days=365)
            elif plan == 'low_income':
                current_user.subscription_type = 'low_income'
                # Set subscription end date to 1 year from now
                # current_user.subscription_end = datetime.utcnow() + timedelta(days=365)
        
        # Commit changes to database
        db.session.commit()
        
        # Clear payment session
        session.pop('payment_info', None)
        
        # Return success to client
        return jsonify({
            'success': True,
            'payment_id': new_payment.id,
            'redirect_url': url_for('paypal.success')
        })
    
    except Exception as e:
        logger.error(f"Error capturing PayPal payment: {str(e)}")
        # Try to rollback the transaction
        try:
            db.session.rollback()
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': 'Server error processing payment'
        }), 500

@paypal_bp.route('/success', methods=['GET'])
@login_required
def success():
    """Display payment success page"""
    return render_template('payment_success.html')

@paypal_bp.route('/cancel', methods=['GET'])
@login_required
def cancel():
    """Display payment cancelled page"""
    # Clear payment session
    session.pop('payment_info', None)
    
    return render_template('payment_cancel.html')

# Main function to register PayPal routes
def register_paypal_routes(app):
    """
    Register all PayPal routes with the Flask app
    This function is called from main.py
    """
    # Check if PayPal routes are already registered
    if hasattr(app, '_paypal_routes_registered') and app._paypal_routes_registered:
        app.logger.info("PayPal routes already registered, skipping")
        return app
        
    app.logger.info("Registering PayPal routes")
    init_paypal_routes(app)
    
    # Mark PayPal routes as registered
    app._paypal_routes_registered = True
    return app

def init_paypal_routes(app):
    """Register PayPal routes with the app"""
    app.register_blueprint(paypal_bp)
    
    # Also make client ID available to all templates
    @app.context_processor
    def inject_paypal_client_id():
        return dict(paypal_client_id=PAYPAL_CLIENT_ID)