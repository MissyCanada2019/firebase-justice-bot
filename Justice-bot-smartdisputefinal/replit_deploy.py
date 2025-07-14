#!/usr/bin/env python3
"""
Replit Deployment Helper for SmartDispute.ai

This script configures the application for proper deployment on Replit,
specifically addressing the port 8080 requirements and ensuring
consistency across development and production environments.
"""
import os
import sys
import logging
import socket
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('deployment')

def check_port(port, host='0.0.0.0'):
    """Check if a port is available on the specified host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0  # Return True if port is in use
    except Exception as e:
        logger.error(f"Error checking port {port}: {e}")
        return False

def check_environment_variables():
    """Check if necessary environment variables are set"""
    required_vars = [
        'DATABASE_URL',
        'SESSION_SECRET'
    ]
    
    optional_vars = [
        'STRIPE_SECRET_KEY',
        'OPENAI_API_KEY',
        'SLACK_BOT_TOKEN',
        'GOOGLE_OAUTH_CLIENT_ID',
        'GOOGLE_OAUTH_CLIENT_SECRET'
    ]
    
    # Check required variables
    missing_required = [var for var in required_vars if not os.environ.get(var)]
    if missing_required:
        logger.error(f"Missing required environment variables: {', '.join(missing_required)}")
        logger.error("Please set these variables in the Replit Secrets tab")
        return False
    
    # Check optional variables
    missing_optional = [var for var in optional_vars if not os.environ.get(var)]
    if missing_optional:
        logger.warning(f"Some optional environment variables are not set: {', '.join(missing_optional)}")
        logger.warning("These variables may be needed for certain functionality")
    
    return True

def run_port8080_server():
    """Run the application on port 8080"""
    try:
        import subprocess
        logger.info("Starting SmartDispute.ai on port 8080...")
        
        # Use Python to run our direct port 8080 server
        process = subprocess.Popen(
            ["python", "main_8080.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait a bit for the server to start
        time.sleep(2)
        
        # Check if it's running
        if check_port(8080):
            logger.info("Server started successfully on port 8080")
            logger.info("Application is now accessible via Replit web interface")
            
            # Log output from the process
            for line in process.stdout:
                print(line, end='')
                
            return True
        else:
            logger.error("Server failed to start on port 8080")
            return False
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return False

def main():
    """Main function"""
    logger.info("\n==========================================")
    logger.info("SmartDispute.ai Replit Deployment Helper")
    logger.info("==========================================\n")
    
    # Check environment variables
    if not check_environment_variables():
        logger.error("Environment check failed, but continuing anyway")
    
    # Check if port 8080 is already in use
    if check_port(8080):
        logger.warning("Port 8080 is already in use, another process may be running")
        logger.warning("Please stop any existing server before continuing")
        sys.exit(1)
    
    # Run the port 8080 server
    success = run_port8080_server()
    
    if success:
        logger.info("Deployment successful!")
    else:
        logger.error("Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
