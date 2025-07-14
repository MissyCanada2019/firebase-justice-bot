import os

# Stripe configuration
STRIPE_PUBLISHABLE_KEY = 'pk_test_51R9jlkPvkARutqYVEa7PkG7ynxJZ8Xc8WKMCpAalvdMgeUeas6A6morMoNti5WmJfCdkm8MAoqodeqcUQGG8DQeK00VTUjO1qh'
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

# PayPal configuration
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')

# OpenAI configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Anthropic configuration (if you decide to use it)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Slack configuration
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN', 'ayWV96D2UHa4tgK0Wfhrb2Dy5fNcaPReMy7PciZGPmQCB2yvODZIEyTn50gun4Z8B00GX4y4vnV')
SLACK_CHANNEL_ID = os.environ.get('SLACK_CHANNEL_ID', '#general')

# Replit domain configuration
REPLIT_DOMAIN = os.environ.get('REPLIT_DOMAINS', '').split(',')[0] if os.environ.get('REPLIT_DOMAINS') else None
REPLIT_DEV_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN')

# Custom domain configuration
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')

# Application configuration
APP_NAME = 'SmartDispute.ai'
APP_VERSION = '1.0.0'
APP_ADMIN_EMAIL = 'smartdisputecanada@gmail.com'

# Feature flags
ENABLE_SLACK_NOTIFICATIONS = True
ENABLE_EMAIL_NOTIFICATIONS = True

# Get the appropriate domain for the application
def get_app_domain():
    """Return the appropriate domain for the application"""
    if os.environ.get('REPLIT_DEPLOYMENT'):
        # Production deployment
        if CUSTOM_DOMAIN:
            return CUSTOM_DOMAIN
        return REPLIT_DOMAIN
    # Development
    return REPLIT_DEV_DOMAIN
