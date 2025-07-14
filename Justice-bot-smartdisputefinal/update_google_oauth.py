#!/usr/bin/env python3
"""
Google OAuth Credentials Update Script for SmartDispute.ai

This script updates the Google OAuth client ID and client secret
environment variables used by the application.
"""
import os
import sys

# IMPORTANT: Never hardcode credentials in the script file
# We'll ask for them at runtime

def update_google_oauth_credentials():
    """Update Google OAuth credentials in environment variables"""
    print("\n=== GOOGLE OAUTH CREDENTIALS UPDATE ===")
    print("This script will update the Google OAuth credentials used by SmartDispute.ai")
    print("\nIMPORTANT: Make sure you have created an OAuth 2.0 Client ID in Google Cloud Console")
    print("with the correct redirect URIs set to:")
    print(f"  - https://{os.environ.get('REPLIT_DEV_DOMAIN')}/google_login/callback")
    
    # Get the current credentials if they exist
    current_client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', 'Not set')
    current_client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'Not set')
    
    print(f"\nCurrent Google OAuth Client ID: {current_client_id}")
    print(f"Current Google OAuth Client Secret: {'*****' if current_client_secret != 'Not set' else 'Not set'}")
    
    # Prompt for new credentials
    print("\nEnter the new credentials (or press Enter to keep current value):")
    new_client_id = input("Client ID: ").strip() or current_client_id
    new_client_secret = input("Client Secret: ").strip() or current_client_secret
    
    # Update the environment variables
    os.environ['GOOGLE_OAUTH_CLIENT_ID'] = new_client_id
    os.environ['GOOGLE_OAUTH_CLIENT_SECRET'] = new_client_secret
    
    print("\n\u2705 Google OAuth credentials updated in the environment")
    print("\nNOTE: These changes will only persist for the current session.")
    print("To make them permanent, you should add them to Replit Secrets or .env file.")
    
    # Print instructions for testing
    print("\n=== TESTING INSTRUCTIONS ===")
    print(f"1. Go to https://{os.environ.get('REPLIT_DEV_DOMAIN')}/login")
    print("2. Click the 'Login with Google' button")
    print("3. You should be redirected to the Google login page")
    print("4. After logging in, you should be redirected back to the application")
    
    return True

def add_google_oauth_environment_variables():
    """Add Google OAuth environment variables to Replit Secrets"""
    # This would use the Replit API to add secrets, but that's beyond
    # the scope of this script. Provide instructions instead.
    print("\n=== MAKE CREDENTIALS PERMANENT ===")
    print("To make these credentials permanent:")
    print("1. Go to the Replit project page")
    print("2. Click on 'Secrets' in the left sidebar")
    print("3. Add the following secrets:")
    print("   - GOOGLE_OAUTH_CLIENT_ID")
    print("   - GOOGLE_OAUTH_CLIENT_SECRET")
    print("4. Set their values to the credentials you entered above")
    print("\nThis will ensure the credentials persist across restarts.")

def main():
    """Main function"""
    if update_google_oauth_credentials():
        add_google_oauth_environment_variables()
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
