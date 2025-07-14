#!/usr/bin/env python3
"""
Slack Notification Service for SmartDispute.ai

This module provides Slack integration for sending notifications about
system activities, errors, and important events.
"""
import os
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Slack client with environment variables
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
SLACK_CHANNEL_ID = os.environ.get('SLACK_CHANNEL_ID', '#general')

if not SLACK_BOT_TOKEN:
    logger.warning("SLACK_BOT_TOKEN not found in environment variables")

# Initialize Slack client if token is available
slack_client = None
if SLACK_BOT_TOKEN:
    slack_client = WebClient(token=SLACK_BOT_TOKEN)

def post_message(message: str, channel: str = None, attachments: List[Dict] = None) -> bool:
    """
    Post a message to a Slack channel
    
    Args:
        message (str): Message text to send
        channel (str, optional): Channel ID to post to. Default is SLACK_CHANNEL_ID from env
        attachments (List[Dict], optional): Slack message attachments
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not slack_client:
        logger.warning("Slack integration not configured. Message not sent.")
        return False
        
    try:
        # Use the specified channel or the default one
        target_channel = channel or SLACK_CHANNEL_ID
        
        # Prepare API call parameters
        params = {
            "channel": target_channel,
            "text": message
        }
        
        # Add attachments if provided
        if attachments:
            params["attachments"] = attachments
            
        # Send the message
        response = slack_client.chat_postMessage(**params)
        
        logger.info(f"Message posted to Slack channel {target_channel}")
        return True
    except SlackApiError as e:
        logger.error(f"Error posting message to Slack: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error posting to Slack: {str(e)}")
        return False
        
def notify_system_event(event_type: str, details: Dict[str, Any]) -> bool:
    """
    Send a notification about a system event
    
    Args:
        event_type (str): Type of event (e.g., 'signup', 'payment', 'error')
        details (Dict): Details about the event
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Create a formatted message based on event type
    if event_type == 'signup':
        message = f":star: *New User Signup!* :star:\n" \
                 f"Name: {details.get('name', 'N/A')}\n" \
                 f"Email: {details.get('email', 'N/A')}\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 
    elif event_type == 'payment':
        message = f":moneybag: *New Payment Received!* :moneybag:\n" \
                 f"User: {details.get('user_email', 'N/A')}\n" \
                 f"Amount: ${details.get('amount', 0):.2f} {details.get('currency', 'CAD')}\n" \
                 f"Payment Type: {details.get('payment_type', 'N/A')}\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 
    elif event_type == 'error':
        message = f":rotating_light: *System Error!* :rotating_light:\n" \
                 f"Error Type: {details.get('error_type', 'Unknown')}\n" \
                 f"Message: {details.get('message', 'N/A')}\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 
    elif event_type == 'document_uploaded':
        message = f":page_facing_up: *New Document Uploaded* :page_facing_up:\n" \
                 f"User: {details.get('user_email', 'N/A')}\n" \
                 f"Document Type: {details.get('doc_type', 'N/A')}\n" \
                 f"Case ID: {details.get('case_id', 'N/A')}\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 
    elif event_type == 'case_created':
        message = f":briefcase: *New Case Created* :briefcase:\n" \
                 f"User: {details.get('user_email', 'N/A')}\n" \
                 f"Case Type: {details.get('case_type', 'N/A')}\n" \
                 f"Case ID: {details.get('case_id', 'N/A')}\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 
    else:
        message = f":information_source: *System Notification* :information_source:\n" \
                 f"Event: {event_type}\n" \
                 f"Details: {json.dumps(details, indent=2)}\n" \
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 
    # Send the notification
    return post_message(message)
    
def notify_error(error_type: str, message: str, details: Dict = None) -> bool:
    """
    Send a notification about an error
    
    Args:
        error_type (str): Type of error (e.g., 'database', 'payment', 'api')
        message (str): Error message
        details (Dict, optional): Additional error details
        
    Returns:
        bool: True if successful, False otherwise
    """
    error_info = {
        'error_type': error_type,
        'message': message
    }
    
    # Add any additional details
    if details:
        error_info.update(details)
        
    return notify_system_event('error', error_info)

def get_channel_history(limit: int = 100) -> Optional[List[Dict]]:
    """
    Get message history from the default channel
    
    Args:
        limit (int): Maximum number of messages to retrieve
        
    Returns:
        List[Dict]: List of message data dictionaries, or None if error
    """
    if not slack_client:
        logger.warning("Slack integration not configured. Cannot retrieve channel history.")
        return None
        
    try:
        response = slack_client.conversations_history(
            channel=SLACK_CHANNEL_ID,
            limit=limit
        )
        
        messages = []
        for msg in response['messages']:
            # Format the message data for easier use
            message_data = {
                'text': msg.get('text', ''),
                'timestamp': datetime.fromtimestamp(float(msg['ts'])).strftime('%Y-%m-%d %H:%M:%S'),
                'user': msg.get('user', ''),
                'bot_id': msg.get('bot_id', None),
                'thread_ts': msg.get('thread_ts', None),
                'reply_count': msg.get('reply_count', 0),
            }
            
            messages.append(message_data)
            
        return messages
    except SlackApiError as e:
        logger.error(f"Error retrieving Slack channel history: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving Slack channel history: {str(e)}")
        return None
