"""Direct Flask entry point for SmartDispute.ai using Flask's development server.

This configuration matches the successful setup that was working 5 days ago on Railway.
"""
from app import app
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("\nStarting Flask development server on port 5000...")
    # Use Flask's built-in development server instead of gunicorn
    # This is the configuration that was working before
    app.run(host="0.0.0.0", port=5000, debug=True)
