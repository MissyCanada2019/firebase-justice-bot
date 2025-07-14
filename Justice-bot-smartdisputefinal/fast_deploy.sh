#!/bin/bash
# Fast deployment script for SmartDispute.ai

# Make the script executable
chmod +x fast_deploy.py

# Set environment variables
export FLASK_ENV=production
export FLASK_DEBUG=0

# Start with optimized launch
echo "Starting SmartDispute.ai with optimized launcher..."
python fast_deploy.py