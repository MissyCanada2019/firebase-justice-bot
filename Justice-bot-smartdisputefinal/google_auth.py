"""
Google OAuth authentication blueprint for SmartDispute.ai
"""
import json
import os

import requests
from flask import Blueprint, redirect, request, url_for, flash, current_app
from flask_login import login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient

from app import db
from models import User

# Google OAuth credentials
GOOGLE_CLIENT_ID = os.environ["GOOGLE_OAUTH_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_OAUTH_CLIENT_SECRET"]
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Log setup instructions
if 'REPLIT_DEV_DOMAIN' in os.environ:
    DEV_REDIRECT_URL = f'https://{os.environ["REPLIT_DEV_DOMAIN"]}/google_login/callback'
else:
    DEV_REDIRECT_URL = 'https://smartdispute.replit.app/google_login/callback'

print(f"""To make Google authentication work:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create or edit your OAuth 2.0 Client ID
3. Add {DEV_REDIRECT_URL} to Authorized redirect URIs

For detailed instructions, see:
https://docs.replit.com/additional-resources/google-auth-in-flask#set-up-your-oauth-app--client
""")

# Create OAuth client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint
google_auth = Blueprint("google_auth", __name__)


@google_auth.route("/google_login")
def login():
    """Route for initiating Google login"""
    # Find out what URL to hit for Google login
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        # Replacing http:// with https:// is important as the external
        # protocol must be https to match the URI whitelisted in Google Console
        redirect_uri=request.base_url.replace("http://", "https://") + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@google_auth.route("/google_login/callback")
def callback():
    """Callback route for Google OAuth"""
    # Get authorization code Google sent back
    code = request.args.get("code")
    if not code:
        flash("Google authentication failed. Please try again.", "danger")
        return redirect(url_for("login"))

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        # Replacing http:// with https:// is important as the external
        # protocol must be https to match the URI whitelisted
        authorization_response=request.url.replace("http://", "https://"),
        redirect_url=request.base_url.replace("http://", "https://"),
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens, let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    userinfo = userinfo_response.json()
    if not userinfo.get("email_verified"):
        flash("User email not verified by Google", "danger")
        return redirect(url_for("login"))

    # Get user info
    users_email = userinfo["email"]
    users_name = userinfo.get("given_name", userinfo.get("name", users_email.split('@')[0]))

    # Check if user exists in database
    user = User.query.filter_by(email=users_email).first()
    if not user:
        # Create a new user
        user = User(
            username=users_name,
            email=users_email,
            password_hash="google-oauth-user"  # This password can never be used to log in
        )
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"Created new user via Google OAuth: {users_email}")

    # Log in the user
    login_user(user)
    flash(f"Successfully logged in as {user.username}", "success")

    # Redirect to dashboard
    return redirect(url_for("dashboard"))


@google_auth.route("/google_logout")
@login_required
def logout():
    """Route for logging out"""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("index"))