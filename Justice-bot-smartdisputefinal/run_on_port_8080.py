"""
Simplified server launcher for SmartDispute.ai
This runs the Flask app directly on port 8080
"""

from app import app
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Print environment information
logging.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
logging.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not found')}")
logging.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not found')}")

# Main entry point
if __name__ == "__main__":
    # Start the Flask app on port 8080
    logging.info("Starting Flask application on port 8080")
    app.run(host="0.0.0.0", port=8080)