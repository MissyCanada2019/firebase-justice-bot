import os
import stripe
import logging
import uuid
from datetime import datetime
from config import STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Stripe with the API key
stripe.api_key = STRIPE_SECRET_KEY

# Domain for redirects
def get_domain():
    """Get the appropriate domain for the environment"""
    replit_domains = os.environ.get('REPLIT_DOMAINS')
    if replit_domains:
        return 'https://' + replit_domains.split(',')[0]
    return 'https://smartdispute.ai'

def create_checkout_session(amount, currency='cad', description='SmartDispute.ai Document Fee', payment_type='document', metadata=None):
    """
    Create a Stripe checkout session for a one-time payment
    
    Args:
        amount (float): Amount to charge
        currency (str): Currency code (default: cad)
        description (str): Description of the payment
        payment_type (str): Type of payment ('document', 'subscription', 'mailing')
        metadata (dict): Additional metadata to store with the payment
        
    Returns:
        dict: Session details including checkout URL or None if error
    """
    try:
        # Convert amount to cents (Stripe requires integer)
        amount_cents = int(amount * 100)
        
        # Default metadata
        if metadata is None:
            metadata = {}
        
        # Add payment type to metadata
        metadata['payment_type'] = payment_type
        
        # Product name based on payment type
        product_names = {
            'document': 'Document Generation',
            'subscription': 'Subscription',
            'mailing': 'Document Mailing Service'
        }
        product_name = product_names.get(payment_type, 'SmartDispute.ai Service')
        
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': product_name,
                            'description': description,
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f"{get_domain()}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{get_domain()}/payment/cancel",
            metadata=metadata,
        )
        
        return {
            'id': checkout_session.id,
            'url': checkout_session.url,
            'amount': amount,
            'currency': currency
        }
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {str(e)}")
        return None

def create_subscription_checkout(price_id, description='SmartDispute.ai Subscription', metadata=None):
    """
    Create a Stripe checkout session for a subscription
    
    Args:
        price_id (str): Stripe Price ID for the subscription
        description (str): Description of the subscription
        metadata (dict): Additional metadata to store with the subscription
        
    Returns:
        dict: Session details including checkout URL or None if error
    """
    try:
        # Default metadata
        if metadata is None:
            metadata = {}
        
        # Add payment type to metadata
        metadata['payment_type'] = 'subscription'
        
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f"{get_domain()}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{get_domain()}/payment/cancel",
            metadata=metadata,
        )
        
        return {
            'id': checkout_session.id,
            'url': checkout_session.url
        }
    except Exception as e:
        logger.error(f"Error creating Stripe subscription checkout: {str(e)}")
        return None

def retrieve_session(session_id):
    """
    Retrieve details of a checkout session
    
    Args:
        session_id (str): Stripe Checkout Session ID
        
    Returns:
        object: Stripe Session object or None if error
    """
    try:
        return stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        logger.error(f"Error retrieving Stripe session: {str(e)}")
        return None

def verify_payment(session_id, expected_amount=None):
    """
    Verify a Stripe payment by checking the session status
    
    Args:
        session_id (str): Stripe Checkout Session ID
        expected_amount (float, optional): Expected payment amount for verification
        
    Returns:
        str: Payment status ('completed', 'pending', 'failed')
    """
    try:
        session = retrieve_session(session_id)
        
        if not session:
            return 'failed'
        
        # Check payment status
        if session.payment_status != 'paid':
            return 'pending'
        
        # Verify payment amount if expected amount is provided
        if expected_amount is not None:
            # Get the actual amount (in dollars) from the session
            # Stripe amounts are in cents, so divide by 100
            actual_amount = session.amount_total / 100.0
            if abs(actual_amount - expected_amount) > 0.01:  # Allow for small rounding differences
                logger.error(f"Payment amount mismatch: expected {expected_amount}, got {actual_amount}")
                return 'failed'
        
        return 'completed'
    except Exception as e:
        logger.error(f"Error verifying Stripe payment: {str(e)}")
        return 'failed'

def create_refund(payment_intent_id, amount=None, reason=None):
    """
    Create a refund for a payment
    
    Args:
        payment_intent_id (str): Stripe Payment Intent ID
        amount (float, optional): Amount to refund (in dollars, if None, full refund)
        reason (str, optional): Reason for the refund
        
    Returns:
        object: Refund object or None if error
    """
    try:
        refund_params = {'payment_intent': payment_intent_id}
        
        # If amount provided, convert to cents
        if amount is not None:
            refund_params['amount'] = int(amount * 100)
            
        # If reason provided, add it
        if reason is not None:
            refund_params['reason'] = reason
            
        return stripe.Refund.create(**refund_params)
    except Exception as e:
        logger.error(f"Error creating Stripe refund: {str(e)}")
        return None

def get_payment_details(payment_intent_id):
    """
    Get details of a payment intent
    
    Args:
        payment_intent_id (str): Stripe Payment Intent ID
        
    Returns:
        object: Payment Intent object or None if error
    """
    try:
        return stripe.PaymentIntent.retrieve(payment_intent_id)
    except Exception as e:
        logger.error(f"Error retrieving Stripe payment details: {str(e)}")
        return None

def create_customer(email, name=None, metadata=None):
    """
    Create a Stripe customer
    
    Args:
        email (str): Customer email
        name (str, optional): Customer name
        metadata (dict, optional): Additional metadata
        
    Returns:
        object: Customer object or None if error
    """
    try:
        customer_params = {
            'email': email
        }
        
        if name:
            customer_params['name'] = name
            
        if metadata:
            customer_params['metadata'] = metadata
            
        return stripe.Customer.create(**customer_params)
    except Exception as e:
        logger.error(f"Error creating Stripe customer: {str(e)}")
        return None

def create_subscription(customer_id, price_id, metadata=None):
    """
    Create a subscription for a customer
    
    Args:
        customer_id (str): Stripe Customer ID
        price_id (str): Stripe Price ID
        metadata (dict, optional): Additional metadata
        
    Returns:
        object: Subscription object or None if error
    """
    try:
        subscription_params = {
            'customer': customer_id,
            'items': [{'price': price_id}],
            'payment_behavior': 'default_incomplete',
            'expand': ['latest_invoice.payment_intent'],
        }
        
        if metadata:
            subscription_params['metadata'] = metadata
            
        return stripe.Subscription.create(**subscription_params)
    except Exception as e:
        logger.error(f"Error creating Stripe subscription: {str(e)}")
        return None

def cancel_subscription(subscription_id):
    """
    Cancel a subscription
    
    Args:
        subscription_id (str): Stripe Subscription ID
        
    Returns:
        object: Subscription object or None if error
    """
    try:
        return stripe.Subscription.delete(subscription_id)
    except Exception as e:
        logger.error(f"Error canceling Stripe subscription: {str(e)}")
        return None

def get_subscription(subscription_id):
    """
    Get subscription details
    
    Args:
        subscription_id (str): Stripe Subscription ID
        
    Returns:
        object: Subscription object or None if error
    """
    try:
        return stripe.Subscription.retrieve(subscription_id)
    except Exception as e:
        logger.error(f"Error retrieving Stripe subscription: {str(e)}")
        return None