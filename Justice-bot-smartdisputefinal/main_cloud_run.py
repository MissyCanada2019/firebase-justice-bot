"""
Cloud Run optimized main entry point for SmartDispute.ai
Single port 8080 deployment without complex port forwarding
"""
import os
import logging
from app_cloud_run import app

# Configure logging for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

if __name__ == '__main__':
    # Cloud Run provides PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    
    # Run application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )