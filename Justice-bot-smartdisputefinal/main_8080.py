"""
Main entry point for SmartDispute.ai running on port 8080
This ensures compatibility with Replit's web interface
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Set port to 8080 for Replit web access
    port = int(os.environ.get('PORT', 8080))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )