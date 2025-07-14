# Import the app for gunicorn
from app import app
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Make sure the app is accessible externally when run through gunicorn
app.config['SERVER_NAME'] = None

# Print out the environment variables related to Replit domains and deployment
logging.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
logging.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not found')}")
logging.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not found')}")

# Always use port 8080 for Replit compatibility
PORT = 8080
logging.info(f"Main port set to: {PORT}")

# Run the Flask app directly if this script is executed
if __name__ == "__main__":
    # Print all registered routes for debugging
    print("\nRegistered routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ','.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"{rule.rule:40s} {methods:20s} -> {rule.endpoint}")
    
    # Start the Flask app on port 8080
    print(f"\nStarting Flask server on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT)