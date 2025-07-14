"""
PayPal Payment Integration Service

This module provides utility functions for working with PayPal payments.
"""

import os
import json
import uuid
import logging
import requests
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# PayPal API endpoints
PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"  # Use sandbox for development
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')

def get_paypal_access_token():
    """Get an access token from PayPal API"""
    try:
        if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
            logger.error("PayPal credentials not configured")
            return None
        
        url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US"
        }
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(
            url,
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            logger.error(f"Failed to get PayPal access token: {response.status_code}, {response.text}")
            return None
    
    except Exception as e:
        logger.error(f"Error getting PayPal access token: {str(e)}")
        return None

def verify_paypal_payment(order_id):
    """
    Verify a PayPal payment by order ID
    
    Args:
        order_id (str): PayPal order ID to verify
        
    Returns:
        dict: Payment details if valid, None if invalid
    """
    try:
        access_token = get_paypal_access_token()
        if not access_token:
            return None
        
        url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            payment_data = response.json()
            
            # Verify payment status
            if payment_data.get('status') != 'COMPLETED':
                logger.warning(f"Payment {order_id} not completed: {payment_data.get('status')}")
                return None
            
            return {
                'paypal_order_id': order_id,
                'status': payment_data.get('status'),
                'amount': payment_data.get('purchase_units', [{}])[0].get('amount', {}).get('value'),
                'currency': payment_data.get('purchase_units', [{}])[0].get('amount', {}).get('currency_code'),
                'payer_id': payment_data.get('payer', {}).get('payer_id'),
                'payer_email': payment_data.get('payer', {}).get('email_address'),
                'payment_time': datetime.utcnow().isoformat(),
                'full_response': payment_data
            }
        else:
            logger.error(f"Failed to verify PayPal payment: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error verifying PayPal payment: {str(e)}")
        return None

def create_paypal_order(amount, currency="CAD", description="SmartDispute.ai Payment"):
    """
    Create a PayPal order server-side
    
    Args:
        amount (str): Payment amount (e.g., '5.00')
        currency (str): Currency code (default: CAD)
        description (str): Payment description
        
    Returns:
        str: Order ID if successful, None if failed
    """
    try:
        access_token = get_paypal_access_token()
        if not access_token:
            return None
        
        url = f"{PAYPAL_BASE_URL}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": amount
                    },
                    "description": description
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            order_data = response.json()
            return order_data.get('id')
        else:
            logger.error(f"Failed to create PayPal order: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating PayPal order: {str(e)}")
        return None

def capture_paypal_order(order_id):
    """
    Capture a PayPal order that was previously created
    
    Args:
        order_id (str): PayPal order ID to capture
        
    Returns:
        dict: Capture details if successful, None if failed
    """
    try:
        access_token = get_paypal_access_token()
        if not access_token:
            return None
        
        url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 201:
            capture_data = response.json()
            return {
                'paypal_order_id': order_id,
                'status': capture_data.get('status'),
                'amount': capture_data.get('purchase_units', [{}])[0].get('payments', {}).get('captures', [{}])[0].get('amount', {}).get('value'),
                'currency': capture_data.get('purchase_units', [{}])[0].get('payments', {}).get('captures', [{}])[0].get('amount', {}).get('currency_code'),
                'capture_id': capture_data.get('purchase_units', [{}])[0].get('payments', {}).get('captures', [{}])[0].get('id'),
                'capture_time': datetime.utcnow().isoformat(),
                'full_response': capture_data
            }
        else:
            logger.error(f"Failed to capture PayPal order: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error capturing PayPal order: {str(e)}")
        return None