"""
Replit-optimized version of main.py with enhanced proxy handling
"""
from app import app
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get Replit domain information
replit_domains = os.environ.get('REPLIT_DOMAINS', 'not-set')
replit_dev_domain = os.environ.get('REPLIT_DEV_DOMAIN', 'not-set')

# Log environment information
logging.info(f"REPLIT_DOMAINS: {replit_domains}")
logging.info(f"REPLIT_DEV_DOMAIN: {replit_dev_domain}")

# Important for Replit: Don't restrict the SERVER_NAME
app.config['SERVER_NAME'] = None

# Important for proper Replit proxy handling
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Ensure templates always use the correct domain
if replit_domains:
    domain = replit_domains.split(',')[0].strip()
    app.config['APPLICATION_ROOT'] = f"https://{domain}"

if __name__ == "__main__":
    print("\nStarting Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)