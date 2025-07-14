# Import the app for gunicorn
from app import app
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Make sure the app is accessible externally when run through gunicorn
app.config['SERVER_NAME'] = None

# Print out the environment variables related to Replit domains and deployment
logging.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
logging.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not found')}")
logging.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not found')}")

# We're running directly on port 8080
PORT = 8080
logging.info(f"Main port selected: {PORT}")

if __name__ == "__main__":
    # If run directly, not through gunicorn
    # Print all registered routes for debugging
    print("\nRegistered routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ','.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"{rule.rule:40s} {methods:20s} -> {rule.endpoint}")
    
    # Start the server on the configured port
    print(f"\nStarting Flask server on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=False)