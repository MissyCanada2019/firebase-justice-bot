# Import the Flask app and run it directly on port 8080
import os
import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Print relevant environment information
    logging.info(f"REPLIT_DEPLOYMENT: {os.environ.get('REPLIT_DEPLOYMENT', 'Not found')}")
    logging.info(f"REPLIT_DOMAINS: {os.environ.get('REPLIT_DOMAINS', 'Not found')}")
    logging.info(f"REPLIT_DEV_DOMAIN: {os.environ.get('REPLIT_DEV_DOMAIN', 'Not found')}")
    
    # Run the app directly on port 8080 for Replit compatibility
    # without any port forwarding or redirection
    logging.info("Starting Flask application directly on port 8080")
    app.run(host="0.0.0.0", port=8080, debug=False)